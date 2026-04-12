import logging
from math import inf

import yfinance as yf

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


# PURPOSE:
#   -ExternalApi provides a external finance fetching abstraction
#   -provides functionality related to fetching live stock data
class ExternalApi:

    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -price(float); live stock price
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -price; current market price for ticker
    # RAISES: None
    @staticmethod
    def get_stock_price(ticker : str) -> float:
        price = yf.Ticker(ticker).fast_info.last_price
        return price


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -exist(bool); whether ticker exists in the open market
    # PRECONDITION:
    #   -ticker; matches format [A-Z]{1,5}
    # POSTCONDITION:
    #   -exist; True if ticker exists in open market, False otherwise
    # RAISES: None
    @staticmethod
    def does_ticker_exist(ticker : str) -> bool:
        try:
            exist = yf.Ticker(ticker).fast_info.last_price is not None
        except Exception:
            exist = False

        return exist


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -max_shares(float); total shares available in open market
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -max_shares; total float shares available in open market for ticker, otherwise inf
    # RAISES: None
    @staticmethod
    def get_float(ticker : str) -> int:
        max_shares = yf.Ticker(ticker).fast_info.get('floatShares')
        return max_shares if max_shares is not None else inf


    # INPUT:
    #   -tickers(list[str]); a list of stock ticker symbols
    # OUTPUT:
    #   -ticker_package(dict[str,float]); live stock prices for all tickers in list
    # PRECONDITION:
    #   -tickers; exist in open market
    # POSTCONDITION:
    #   -ticker_package; holds current market prices for tickers and the ticker symbol related
    # RAISES: None
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}
        ticker_dat = yf.Tickers(" ".join(tickers))
        
        for t in tickers:
            price = ticker_dat.tickers[t].fast_info.last_price

            if not price:
                price = ExternalApi.get_stock_price(t)

            ticker_package[t] = price

        return ticker_package