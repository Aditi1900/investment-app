import time
import threading

from threading import Lock
from collections import defaultdict

from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "float" : None, "timestamp" : None})
cache_lock = Lock()

# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers un-updated >1sec are removed, simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        expired = []
        now = time.time()
        with cache_lock:
            for ticker, data in cache.items():
                timestamp = data["timestamp"]
                price = data["price"]

                if timestamp is None or price is None:
                    continue

                if now - timestamp > 1: 
                    expired.append(ticker)
                else:  
                   data["price"] += inject_volatility(price)

            for ticker in expired:
                del cache[ticker]

        time.sleep(1)

threading.Thread(target = run, daemon = True).start()



# PURPOSE:
#   -LiveCache provides a cache access abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective fields in ExternalApi.get_stock_price()
    @staticmethod
    def get_stock_price(ticker : str) -> float:

        with cache_lock:
            if cache[ticker]["price"] is None:
                cache[ticker]["price"] = eapi.get_stock_price(ticker)
                cache[ticker]["timestamp"] = time.time()

            price = cache[ticker]["price"]

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective fields in ExternalApi.does_ticker_exist()
    @staticmethod
    def does_ticker_exist(ticker : str) -> bool:
        exist = True

        if ticker not in cache:
            exist = eapi.does_ticker_exist(ticker)

        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective fields in ExternalApi.get_float()
    @staticmethod
    def get_float(ticker : str) -> int:
        
        with cache_lock:
            if cache[ticker]["float"] is None:
                cache[ticker]["float"] = eapi.get_float(ticker)

            max_shares = cache[ticker]["float"]

        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective fields in ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        with cache_lock:
            cached_tickers = list(set(tickers) & set(cache))
            missing_tickers = list(set(tickers) - set(cache))

        fresh = eapi.get_stock_prices(missing_tickers)

        with cache_lock:
            for ticker, price in fresh.items():
                cache[ticker]["price"] = price
                cache[ticker]["timestamp"] = time.time()

            for ticker in cached_tickers:
                ticker_package[ticker] = cache[ticker]["price"]

        ticker_package |= fresh

        return ticker_package





    