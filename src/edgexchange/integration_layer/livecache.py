import time
import threading

from threading import Lock, Condition
from collections import defaultdict, deque

from ..common.errors import FetchingError, LiveCacheError
from ..common import constants
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Condition(Lock())

fetch_locks = {
    "bulk" : Lock(),
    "price":  Lock(),
    "quote":  Lock(),
    "float":  Lock(),
    "sector": Lock(),
    "exists": Lock(),
}


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers prices un-updated >1sec are removed (quotes removed >120sec), simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        expired_price = []
        expired_quote = []
        now = time.time()

        with cache_lock:
            for ticker, data in cache.items():
                price = data["price"]
                quote = data["quote"]
                timestamp = data["timestamp"]
                quote_timestamp = data["quote_timestamp"]

                if price is None:
                    continue

                data["price"] += inject_volatility(price)

                if now - timestamp > constants.PRICE_REFRESH_INTERVAL:
                    expired_price.append(ticker)

                if quote is None:
                    continue

                quote["price"] = data["price"]

                if now - quote_timestamp > constants.QUOTE_REFRESH_INTERVAL:
                    expired_quote.append(ticker)

            for ticker in expired_quote:
                cache[ticker]["quote"] = None
                cache[ticker]["quote_timestamp"] = None

            for ticker in expired_price:
                cache[ticker]["price"] = None
                cache[ticker]["timestamp"] = None

        elapsed = time.time() - now
        time.sleep(max(0, constants.PRICE_REFRESH_INTERVAL - elapsed))

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
        write = False
        try:

            with fetch_locks["price"]:
                with cache_lock:
                    price = cache.get(ticker, {}).get("price")

                if price is None:
                    price = eapi.get_stock_price(ticker)

                    write = True
                
                with cache_lock:
                    satisfied = cache_lock.wait_for(lambda: cache.get(ticker, {}).get("quote") is not None, timeout=constants.TIMEOUT)
                    
                    if satisfied and write:
                        cache[ticker]["price"] = price
                        cache[ticker]["timestamp"] = time.time()
                        

        except FetchingError as e:
            raise LiveCacheError("Failed to find stocks price") from e

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.does_ticker_exist()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.does_ticker_exist()
    @staticmethod
    def does_ticker_exist(ticker: str) -> bool:
        exist = True

        try:

            with fetch_locks["exists"]:
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

            with fetch_locks["float"]:
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

            with fetch_locks["sector"]:
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
        write = False
        try:
            with fetch_locks["quote"]:
                with cache_lock:
                    stock_info = cache.get(ticker, {}).get("quote")

                if stock_info is None:
                    stock_info = eapi.get_stock_info(ticker)

                    write = True
                        
                with cache_lock:
                    satisfied = cache_lock.wait_for(lambda: cache.get(ticker, {}).get("price") is not None, timeout=constants.TIMEOUT)
                                 
                    if satisfied:
                        stock_info["price"] = cache.get(ticker, {}).get("price")

                    if write:
                        cache[ticker]["quote"] = stock_info
                        cache[ticker]["quote_timestamp"] = time.time()
              

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch stock info") from e

        return stock_info


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_prices()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        try:

            with fetch_locks["bulk"]:
                with cache_lock:
                    cached_tickers = [t for t in tickers if cache.get(t, {}).get("price") is not None]
                    missing_tickers = [t for t in tickers if cache.get(t, {}).get("price") is None]

                    for ticker in cached_tickers:
                        ticker_package[ticker] = cache.get(ticker, {}).get("price")
                
                fresh = eapi.get_stock_prices(missing_tickers)
             
                with cache_lock:
                    for ticker, price in fresh.items():
                        cache[ticker]["price"] = price
                        cache[ticker]["timestamp"] = time.time()
                        ticker_package[ticker] = cache.get(ticker, {}).get("price")
                    cache_lock.notify_all()

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch requested stock prices") from e

        return ticker_package