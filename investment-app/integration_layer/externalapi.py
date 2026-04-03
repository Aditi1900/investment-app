import yfinance as yf


# PURPOSE:
#   -ExternalApi provides a external finance fetching abstraction
#   -provides functionality related to fetching live stock data
class ExternalApi:

    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -price(int); a live stock price
    # PRECONDITION:
    #   -ticker; ticker symbol is a real ticker in open market
    # POSTCONDITION:
    #   -price; corresponding live ticker price has been fetched from yfinance
    # RAISES: None
    @staticmethod
    def get_stock_price(ticker : str) -> int:
        # TODO: Pull stock price data given a ticker
        pass


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -exist(bool); True or False
    # PRECONDITION:
    #   -ticker; matches basic format with <= 5 capital chars
    # POSTCONDITION:
    #   -exist; ticker is identified as being a real(True) or fake(False)
    # RAISES: None
    @staticmethod
    def does_ticker_exist(ticker : str) -> bool:
        # TODO: Call the api to identify if the ticker actually exists
        pass


    # INPUT:
    #   -ticker(str); a stock ticker symbol 
    # OUTPUT:
    #   -max_shares(int); the maximum amount of open market shares
    # PRECONDITION:
    #   -ticker; is an existant ticker in open market
    # POSTCONDITION:
    #   -max_shares; the maximum open market shares is sourced and returned
    # RAISES: None
    @staticmethod
    def get_float(ticker : str) -> int:
        #TODO: Call the api to identify the maximum amount of shares the market has to offer
        pass