import time
import threading

from threading import Lock
from collections import defaultdict

from ..common.errors import FetchingError, LiveCacheError
from ..common.constants import PRICE_REFRESH_INTERVAL, QUOTE_REFRESH_INTERVAL
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Lock()

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
        expired_p = []
        expired_q = []
        now = time.time()
        with cache_lock:
            for ticker, data in cache.items():
                
                #Stock price eviction/refresh policy
                price = data["price"]
                timestamp = data["timestamp"]

                if timestamp is None or price is None:
                    continue

                if now - timestamp > PRICE_REFRESH_INTERVAL: 
                    expired_p.append(ticker)
                else:  
                   data["price"] += inject_volatility(price)

                
                #Stock info quote eviciton/refresh policy
                quote = data["quote"]
                quote_timestamp = data["quote_timestamp"]

                if quote is None or quote_timestamp is None:
                    continue

                if now - quote_timestamp > QUOTE_REFRESH_INTERVAL:
                    expired_q.append(ticker)

            #Cache evictions
            for ticker in expired_q:
                cache[ticker]["quote"] = None
                cache[ticker]["quote_timestamp"] = None

        with fetch_locks["bulk"], cache_lock:
            for ticker in expired_p:
                cache[ticker]["price"] = None
                cache[ticker]["timestamp"] = None

                

        time.sleep(1)

threading.Thread(target = run, daemon = True).start()



# PURPOSE:
#   -LiveCache provides a cache access abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_price()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_price()
    @staticmethod
    def get_stock_price(ticker : str) -> float:
        try:

            with fetch_locks["price"]:
                    with cache_lock:
                        price = cache[ticker]["price"]
                
                    if price is None:
                        price = eapi.get_stock_price(ticker)

                        with cache_lock:
                            cache[ticker]["price"] = price
                            cache[ticker]["timestamp"] = time.time()

        except FetchingError as e:
            raise LiveCacheError("Failed to find stocks price") from e

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.does_ticker_exist()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.does_ticker_exist()
    @staticmethod
    def does_ticker_exist(ticker : str) -> bool:
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
    def get_float(ticker : str) -> int:
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
    def get_sector(ticker : str):
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
        try:

            with fetch_locks["quote"]:
                with cache_lock:
                    stock_info = cache[ticker]["quote"]

                if stock_info is None:
                    stock_info = eapi.get_stock_info(ticker)

                    with cache_lock:
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
                    cached_tickers = [t for t in tickers if cache[t]["price"] is not None]
                    missing_tickers = [t for t in tickers if cache[t]["price"] is None]

                    for ticker in cached_tickers:
                        ticker_package[ticker] = cache[ticker]["price"]

                
                if missing_tickers:
                    fresh = eapi.get_stock_prices(missing_tickers)

                
                    with cache_lock:
                        for ticker, price in fresh.items():
                            cache[ticker]["price"] = price
                            cache[ticker]["timestamp"] = time.time()

                
                    ticker_package |= fresh

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch requested stock prices") from e

        return ticker_package