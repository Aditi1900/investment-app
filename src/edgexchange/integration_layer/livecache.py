import time
import threading

from threading import RLock, Lock, Condition
from collections import defaultdict
from datetime import date


from ..common.errors import FetchingError, LiveCacheError
from ..common.constants import PRICE_REFRESH_INTERVAL, selfexp
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi



cache = defaultdict(lambda : {"price" : None, "quote" : None, "quote_date" : None, "last_accessed" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})

_lock = RLock()
cache_lock = Condition(_lock)

# INPUT:
#    - ticker(str); ticker symbol to update
#    - price(float); price to inject into quote
# OUTPUT: None
# PRECONDITION:
#    - cache[ticker]["quote"]; must not be None
# POSTCONDITION:
#    - cache; quote["price"] updated to price for ticker
# RAISES: None
def sync_price(ticker: str, price: float) -> None:
    cache[ticker]["quote"]["price"] = price


# INPUT:
#    - ticker(str); ticker symbol to update
#    - quote(dict); quote data to write
# OUTPUT: None
# PRECONDITION:
#    - ticker; must exist in cache
# POSTCONDITION:
#    - cache; quote, quote_date, and last_accessed updated for ticker
# RAISES: None
def write_quote(ticker: str, quote: dict) -> None:
    cache[ticker]["quote"] = quote
    cache[ticker]["quote_date"] = date.today()


# INPUT:
#    - ticker(str); ticker symbol to update
#    - price(float); price to write
# OUTPUT: None
# PRECONDITION:
#    - ticker; must exist in cache
#    - cache[ticker]["quote"]; must not be None (sync_price precondition)
# POSTCONDITION:
#    - cache; price, quote["price"], and last_accessed updated for ticker
# RAISES: None
def write_price(ticker: str, price: float) -> None:
    price += inject_volatility(price)
    sync_price(ticker, price)
    cache[ticker]["price"] = price


# INPUT:
#    - key(str); ticker symbol to look up
#    - value(str); field name to retrieve
# OUTPUT:
#    - result(any); value at cache[key][value], or None if key or field not found
# PRECONDITION: None
# POSTCONDITION: None
# RAISES: None
def read(key : str, value : str) -> any:
    return cache.get(key, {}).get(value)


# INPUT:
#    - ticker(str); ticker symbol to stamp
# OUTPUT: None
# PRECONDITION:
#    - ticker; must exist in cache
# POSTCONDITION:
#    - cache; last_accessed updated to current time for ticker
# RAISES: None
def stamp(ticker: str) -> None:
    cache[ticker]["last_accessed"] = time.time()

    
# INPUT:
#    - keys(list[str]); ticker symbols to register in cache
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#    - cache; all tickers in keys exist with default values
#    - cache; last_accessed stamped for all tickers to signal demand
# RAISES: None
def touch(keys: list[str]) -> None:
    for key in keys:
        _ = cache[key]
        stamp(key)


# INPUT:
#    - ticker(str); ticker symbol to remove
# OUTPUT: None
# PRECONDITION:
#    - ticker; must exist in cache
# POSTCONDITION:
#    - cache; ticker and all associated data removed
# RAISES:
#    - KeyError; ticker not in cache
def rm(ticker : str) -> None:
    del cache[ticker]


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#    - cache; quotes refreshed daily via eapi.get_stock_info for any ticker with missing or stale quote
#    - cache; prices refreshed every PRICE_REFRESH_INTERVAL seconds via eapi.get_stock_prices for all tickers
#    - cache; all waiters on cache_lock notified after each price update or on FetchingError
#    - cache; tickers that fail quote fetching with no existing quote are removed
# RAISES: None
def run():
    signal = Condition(_lock)
    while True:
        latency = 0
        start = time.time()

        hot = set()
        expired = set()
        with cache_lock:

            for ticker in cache.keys():
                is_hot = read(ticker, "price") is None or read(ticker, "last_accessed") < start - selfexp(PRICE_REFRESH_INTERVAL)
                is_expired = read(ticker, "quote") is None or read(ticker, "quote_date") < date.today()

                if is_hot:
                    hot.add(ticker)

                if is_hot and is_expired:
                    expired.add(ticker)

        
        def fetch_info():
            if expired:
                try:
 
                    stock_info = eapi.get_stock_info(expired)

                except FetchingError as e:
                    with cache_lock:
                        if e.ticker and read(e.ticker, "quote") is None:
                            rm(e.ticker)
                        cache_lock.notify_all()
                        signal.notify_all()
                    return
            
                with cache_lock:
                    for ticker, quote in stock_info.items():
                        write_quote(ticker, quote)
                        signal.notify_all()

        t1 = threading.Thread(target = fetch_info)
        t1.start()


        def fetch_prices():
            if hot:
                ticker_prices = eapi.get_stock_prices(hot)

                with cache_lock:
                    for ticker, price in ticker_prices.items():
                        signal.wait_for(lambda: read(ticker, "quote") is not None)
                        write_price(ticker, price)
                        cache_lock.notify_all()

        t2 = threading.Thread(target = fetch_prices)
        t2.start()


        t1.join()
        t2.join()
                                 
        end = time.time()
        latency = end - start

        time.sleep(max(0, PRICE_REFRESH_INTERVAL - latency))

threading.Thread(target = run, daemon = True).start()



# PURPOSE:
#   -LiveCache provides a cache access abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_price()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_price()
    @staticmethod
    def get_stock_price(ticker: str) -> float:
        
        with cache_lock:
            touch([ticker])
            cache_lock.wait_for(lambda : read(ticker, "price") is not None)
            price = read(ticker, "price")

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.does_ticker_exist()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.does_ticker_exist()
    @staticmethod
    def does_ticker_exist(ticker: str) -> bool:
        exist = True

        try:

            if ticker not in cache:
                exist = eapi.does_ticker_exist(ticker)

        except FetchingError as e:
            raise LiveCacheError("Ticker search failed") from e

        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_float()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_float()
    @staticmethod
    def get_float(ticker: str) -> int:
        try:

            if persistent_cache[ticker]["float"] is None:
                persistent_cache[ticker]["float"] = eapi.get_float(ticker)

            max_shares = persistent_cache[ticker]["float"]

        except FetchingError as e:
            raise LiveCacheError("Float shares search failed") from e

        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_sector()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_sector()
    @staticmethod
    def get_sector(ticker: str):
        try:

            if persistent_cache[ticker]["sector"] is None:
                persistent_cache[ticker]["sector"] = eapi.get_sector(ticker)

            sector = persistent_cache[ticker]["sector"]

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch stock sector") from e

        return sector


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_info()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_info()
    @staticmethod
    def get_stock_info(ticker: str):
        with cache_lock:
            touch([ticker])
            cache_lock.wait_for(lambda: read(ticker, "quote") is not None)
            stock_info = read(ticker, "quote")
        return stock_info


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_prices()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        
        ticker_package = {}

        with cache_lock:
            touch(tickers)
            for ticker in tickers:
                cache_lock.wait_for(lambda: read(ticker, "price") is not None)
                ticker_package[ticker] = read(ticker, "price")

        return ticker_package