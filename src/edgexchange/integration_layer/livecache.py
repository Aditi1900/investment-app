import time

from collections import defaultdict

from .externalapi import ExternalApi as eapi

# PURPOSE:
#   -LiveCache provides a recent memory abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:
    
    def __init__(self):
        self.cache = defaultdict(lambda : {"price" : None, "float" : None, "timestamp" : None})


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_stock_price(self, ticker : str) -> float:
        if self.cache[ticker]["price"] is None:
            self.cache[ticker]["price"] = eapi.get_stock_price(ticker)
            self.cache[ticker]["timestamp"] = time.time()

        price = self.cache[ticker]["price"]

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def does_ticker_exist(self, ticker : str) -> bool:
        exist = True

        if ticker not in self.cache:
            exist = eapi.does_ticker_exist(ticker)

        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_float(self, ticker : str) -> int:
        if self.cache[ticker]["float"] is None:
            self.cache[ticker]["float"] = eapi.get_float(ticker)

        max_shares = self.cache[ticker]["float"]

        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_stock_prices(self, tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        cached_tickers = list(set(tickers) & set(self.cache))
        missing_tickers = list(set(tickers) - set(self.cache))

        for ticker in cached_tickers:
            ticker_package[ticker] = self.cache[ticker]["price"]
        
        fresh = eapi.get_stock_prices(missing_tickers)
        
        for ticker, price in fresh.items():
            self.cache[ticker]["price"] = price
            self.cache[ticker]["timestamp"] = time.time()

        ticker_package |= fresh

        return ticker_package