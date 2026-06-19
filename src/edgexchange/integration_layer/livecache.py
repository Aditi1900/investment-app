from ast import Constant
import time
import threading

from threading import Lock, Condition
from collections import defaultdict
from datetime import date

from yfinance import live

from ..common.errors import FetchingError, LiveCacheError
from ..common import PRICE_REFRESH_INTERVAL, constants
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})

persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Condition(Lock())


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers prices un-updated >1sec are removed (quotes removed >120sec), simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        try:
            start = time.time()

            expired = []
            with cache_lock:
                for ticker, cache_item in cache.items():
                    if cache_item.get("quote") is None or date.fromtimestamp(cache_item.get("quote_timestamp")) < date.today():
                        expired.append(ticker)

            if expired:
                
                
                try:
                    stock_info = eapi.get_stock_info(expired)
                except FetchingError as e:
                    if e.ticker:
                        with cache_lock:
                            if not cache.get(e.ticker, {}).get("quote"),:
                                del cache[e.ticker]
                    raise
              

            
                with cache_lock:
                    for ticker, quote in stock_info.items():
                        cache[ticker]["quote"] = quote
                        cache[ticker]["quote_timestamp"] = time.time()
                
            
        
            ticker_prices = eapi.get_stock_prices(list(cache.keys()))

            with cache_lock:
                for ticker, price in ticker_prices.items():
                    price += inject_volatility(price)


                    if cache[ticker].get("quote") is not None:
                        cache[ticker]["quote"]["price"] = price


                    cache[ticker]["price"] = price
                    cache[ticker]["timestamp"] = time.time()

                
                cache_lock.notify_all()


            end = time.time()
            latency = end - start
        
        except FetchingError as e:
            pass

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
            cache_item = cache[ticker]
            cache_lock.wait_for(lambda ci=cache_item: ci.get("price") is not None)
            price = cache_item.get("price")

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
            cache_item = cache[ticker]
            cache_lock.wait_for(lambda ci=cache_item: ci.get("quote") is not None)
            stock_info = cache_item.get("quote")

        return stock_info


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_prices()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:

        if not tickers:
            return {}

        ticker_package = {}

        with cache_lock:
            for ticker in tickers:
                _ = cache[ticker]

            for ticker in tickers:
                cache_item = cache[ticker]
                cache_lock.wait_for(lambda ci=cache_item: ci.get("price") is not None)
                ticker_package[ticker] = cache_item.get("price")

        return ticker_package