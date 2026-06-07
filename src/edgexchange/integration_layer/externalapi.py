import logging
from math import inf

import yfinance as yf
from ..common.errors import FetchingError 
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
    # RAISES: 
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def get_stock_price(ticker : str) -> float:
        try:

            price = yf.Ticker(ticker).fast_info.last_price

        except Exception as e:
            raise FetchingError(f"get_stock_price failed: {e}") from e

        return price


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -exist(bool); whether ticker exists in the open market
    # PRECONDITION:
    #   -ticker; matches format [A-Z]{1,5}
    # POSTCONDITION:
    #   -exist; True if ticker exists in open market, False otherwise
    # RAISES: 
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def does_ticker_exist(ticker : str) -> bool:
        try:

            exist = yf.Ticker(ticker).fast_info.last_price is not None

        except Exception as e:
            raise FetchingError(f"does_ticker_exist failed: {e}") from e

        return exist


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -max_shares(float); total shares available in open market
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -max_shares; total float shares available in open market for ticker, otherwise inf
    # RAISES: 
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def get_float(ticker : str) -> int:
        try:

            max_shares = yf.Ticker(ticker).fast_info.get('floatShares')

        except Exception as e:
            raise FetchingError(f"get_float failed: {e}") from e

        return max_shares if max_shares is not None else inf


    # INPUT:
    #   -tickers(list[str]); a list of stock ticker symbols
    # OUTPUT:
    #   -ticker_package(dict[str,float]); live stock prices for all tickers in list
    # PRECONDITION:
    #   -tickers; exist in open market
    # POSTCONDITION:
    #   -ticker_package; holds current market prices for tickers and the ticker symbol related
    # RAISES: 
    #   -FetchingError; if yfinance call fails at any point
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        try:

            ticker_dat = None if not tickers else yf.Tickers(" ".join(tickers))
        
            for t in tickers:
                price = ticker_dat.tickers[t].fast_info.last_price

                if not price:
                    price = yf.Ticker(t).fast_info.last_price

                if not price:
                    raise Exception(t)

                ticker_package[t] = price

        except Exception as e:
            raise FetchingError(f"get_stock_prices failed: {e}") from e

        return ticker_package