import time
import threading
import random

from threading import RLock, Lock, Condition
from collections import defaultdict
from datetime import date


from ..common.errors import FetchingError, LiveCacheError
from ..common import constants
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi



cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})

_lock = RLock()
cache_lock = Condition(_lock)

# INPUT: if N/A - None
#    - key(str); ticker symbol to look up
#    - value(str); field name to retrieve
# OUTPUT:
#    - result(any); value at cache[key][value], or None if key or field not found
# PRECONDITION: None
# POSTCONDITION: None
# RAISES: None
def read(key, value):
    return cache.get(key, {}).get(value)


# INPUT:
#    - keys(list[str]); ticker symbols to register in cache
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#    - cache; all tickers in keys exist with default values
# RAISES: None
def touch(keys):
    for key in keys:
        _ = cache[key]


# INPUT:
#    - keys(list); path of keys to traverse to write location
#    - value(any); value to write
# OUTPUT: None
# PRECONDITION:
#    - keys; len > 0
#    - keys[:-1]; all intermediate keys must already exist in cache
# POSTCONDITION:
#    - cache; value written at location described by keys
# RAISES: None
def write(keys, value):
    loc = cache

    for key in keys[:-1]:
        loc = loc[key]

    loc[keys[-1]] = value


# INPUT:
#    - ticker(str); ticker symbol to remove
# OUTPUT: None
# PRECONDITION:
#    - ticker; must exist in cache
# POSTCONDITION:
#    - cache; ticker and all associated data removed
# RAISES:
#    - KeyError; ticker not in cache
def rm(ticker):
    del cache[ticker]


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#    - cache; quotes refreshed daily via eapi.get_stock_info for any ticker with missing or stale quote
#    - cache; prices refreshed every PRICE_REFRESH_INTERVAL seconds via eapi.get_stock_prices for all tickers
#    - cache; simulated volatility injected into each price update
#    - cache; all waiters on cache_lock notified after each price update or on FetchingError
#    - cache; tickers that fail quote fetching with no existing quote are removed
# RAISES: None
def run():
    signal = Condition(_lock)
    while True:
        latency = 0
        start = time.time()

        expired = []
        with cache_lock:

            for ticker in cache.keys():
                if read(ticker, "quote") is None or date.fromtimestamp(read(ticker, "quote_timestamp")) < date.today():
                    expired.append(ticker)

        
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
                        write([ticker, "quote"], quote)
                        write([ticker, "quote_timestamp"], time.time())
                        signal.notify_all()

        t1 = threading.Thread(target = fetch_info)
        t1.start()


        def fetch_prices():
            ticker_prices = eapi.get_stock_prices(list(cache.keys()))

            with cache_lock:
                for ticker, price in ticker_prices.items():
                    price += inject_volatility(price)
                    signal.wait_for(lambda: read(ticker, "quote") is not None or ticker not in cache)
                    if ticker not in cache: continue
                
                    write([ticker, "quote", "price"], price)
                    write([ticker, "price"], price)
                    write([ticker, "timestamp"], time.time())
                    cache_lock.notify_all()

        t2 = threading.Thread(target = fetch_prices)
        t2.start()


        t1.join()
        t2.join()
                                 
        end = time.time()
        latency = end - start

        time.sleep(max(0, constants.PRICE_REFRESH_INTERVAL - latency))

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