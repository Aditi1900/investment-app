import time
import threading

from threading import Lock
from collections import defaultdict

from ..common.errors import FetchingError, LiveCacheError
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Lock()

# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers un-updated >1sec are removed, simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        expired_p = []
        expired_q = []
        now = time.time()
        with cache_lock:
            for ticker, data in cache.items():
                timestamp = data["timestamp"]
                price = data["price"]

                if timestamp is None or price is None:
                    continue

                if now - timestamp > 1: 
                    expired_p.append(ticker)
                else:  
                   data["price"] += inject_volatility(price)

                
                quote = data["quote"]
                quote_timestamp = data["quote_timestamp"]

                if quote is None or quote_timestamp is None:
                    continue

                if now - quote_timestamp > 120:
                    expired_q.append(ticker)


            for ticker in expired_p:
                cache[ticker]["price"] = None
                cache[ticker]["timestamp"] = None

            for ticker in expired_q:
                cache[ticker]["quote"] = None
                cache[ticker]["quote_timestamp"] = None

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

            with cache_lock:
                if cache[ticker]["price"] is None:
                    cache[ticker]["price"] = eapi.get_stock_price(ticker)
                    cache[ticker]["timestamp"] = time.time()

                price = cache[ticker]["price"]

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

            if persistent_cache[ticker]["float"] is None:
                persistent_cache[ticker]["float"] = eapi.get_float(ticker)

            max_shares = persistent_cache[ticker]["float"]

        except FetchingError as e:
            raise LiveCacheError("Float shares search failed") from e

        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_prices()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        with cache_lock:
            cached_tickers = [t for t in tickers if cache[t]["price"] is not None]
            missing_tickers = [t for t in tickers if cache[t]["price"] is None]

            for ticker in cached_tickers:
                ticker_package[ticker] = cache[ticker]["price"]

        try:

            fresh = eapi.get_stock_prices(missing_tickers)

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch requested stock prices") from e

        with cache_lock:
            for ticker, price in fresh.items():
                cache[ticker]["price"] = price
                cache[ticker]["timestamp"] = time.time()

            

        ticker_package |= fresh

        return ticker_package


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_info()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_info()
    @staticmethod
    def get_stock_info(ticker: str):
        try:
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


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_sector()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_sector()
    @staticmethod
    def get_sector(ticker : str):
        try:
            with cache_lock:
                if persistent_cache[ticker]["sector"] is None:
                    persistent_cache[ticker]["sector"] = eapi.get_sector(ticker)
            
                sector = persistent_cache[ticker]["sector"]

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch stock sector") from e
    
        return sector