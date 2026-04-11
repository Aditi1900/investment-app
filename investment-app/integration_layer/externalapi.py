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
        price = yf.Ticker(ticker).fast_info['last_price']
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
            exist = yf.Ticker(ticker).fast_info['last_price'] is not None
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
    #   -max_shares; total float shares available in open market for ticker
    # RAISES: None
    @staticmethod
    def get_float(ticker : str) -> int:

        try:
            max_shares = yf.Ticker(ticker).info['floatShares']
        except Exception:
            max_shares = inf

        return max_shares