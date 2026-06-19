import time
import threading

from threading import Lock, Condition
from collections import defaultdict
from datetime import date
from typing import NamedTuple

from ..common.errors import FetchingError, LiveCacheError
from ..common import constants
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi



cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Condition(Lock())

def read(key, value):
    return cache.get(key, {}).get(value)

def touch(keys):
    for key in keys:
        _ = cache[key]

def write(keys, value):
    loc = cache

    for key in keys[:-1]:
        loc = loc[key]

    loc[keys[-1]] = value


def rm(ticker):
    del cache[ticker]


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers prices un-updated >1sec are removed (quotes removed >120sec), simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        latency = 0
        try:
            start = time.time()

            expired = []
            with cache_lock:
                for ticker in cache.keys():
                    if read(ticker, "quote") is None or date.fromtimestamp(read(ticker, "quote_timestamp")) < date.today():
                        expired.append(ticker)

            if expired:
                try:

                    stock_info = eapi.get_stock_info(expired)

                except FetchingError as e:
                    with cache_lock:
                        if e.ticker and read(e.ticker, "quote") is None:
                            rm(e.ticker)
                    raise
              

            
                with cache_lock:
                    for ticker, quote in stock_info.items():
                        write([ticker, "quote"], quote)
                        write([ticker, "quote_timestamp"], time.time())
                
            
        
            ticker_prices = eapi.get_stock_prices(list(cache.keys()))

            with cache_lock:
                for ticker, price in ticker_prices.items():
                    price += inject_volatility(price)


                    if read(ticker, "quote") is not None:
                        write([ticker, "quote", "price"], price)


                    write([ticker, "price"], price)
                    write([ticker, "timestamp"], time.time())

                
                cache_lock.notify_all()


            end = time.time()
            latency = end - start
        
        except FetchingError as e:
            with cache_lock:
                cache_lock.notify_all()

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

        if not tickers:
            return {}

        ticker_package = {}

        with cache_lock:
            touch(tickers)
            for ticker in tickers:
                cache_lock.wait_for(lambda: read(ticker, "price") is not None)
                ticker_package[ticker] = read(ticker, "price")

        return ticker_package