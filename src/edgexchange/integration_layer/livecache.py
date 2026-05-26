from .externalapi import ExternalApi as eapi

# PURPOSE:
#   -LiveCache provides a recent memory abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:

    def __init__():
        cache = {}

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_stock_price(self, ticker : str) -> float:
        price = eapi.get_stock_price(ticker)
        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def does_ticker_exist(self, ticker : str) -> bool:
        exist = eapi.does_ticker_exist(ticker)
        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_float(self, ticker : str) -> int:
        max_shares = eapi.get_float(ticker)
        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective ExternalApi.get_stock_price() fields
    def get_stock_prices(self, tickers: list[str]) -> dict[str, float]:
        ticker_package = eapi.get_stock_prices(tickers)
        return ticker_package