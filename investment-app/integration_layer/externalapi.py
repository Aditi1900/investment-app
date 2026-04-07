import yfinance as yf


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
        # TODO: Pull stock price data given a ticker
        pass


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
        # TODO: Call the api to identify if the ticker actually exists
        pass


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
        #TODO: Call the api to identify the maximum amount of shares the market has to offer
        pass