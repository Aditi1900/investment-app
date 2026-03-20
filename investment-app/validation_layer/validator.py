from integration_layer import Api as api


# PURPOSE:
class Validator:
    def __init__(self, service):
        self.serv = service


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def account_validator(self, credentials : tuple[str, str], new : bool) -> bool:
        # TODO: Validate account credentials using service method
        # TODO: Add any other validation you want, if you want to enforce certain additional constraints
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def portfolio_validator(user_account, portfolio_name : str, create : bool) -> bool:
        # TODO: Validate that portfolio_name doesnt already exist
        # TODO: Add any other validation you want, AKA empty name insert
        # TODO: ensure creation only is allowed when portfolio doesnt exist and removal is only allowed when it does
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def stock_ticker_validator(portfolio, ticker : str, purchase : bool) -> bool:
        # TODO: Validate ticker symbol format with regex
        # TODO: identify if we are purchasing a stock or not
        # TODO: if stock is not being purchased check if it exists in the portfolio
        # TODO: if stock is being purchased find out if it exists in yfinance
        # TODO: if ticker doesnt exist in portfolio and we arent purchasing return false
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def stock_quantity_validator(portfolio, shares_requested : tuple[str, int], purchase : bool) -> bool:
        # TODO: If we are not purchasing check if portfolio has enough shares of stock
        # TODO: (optional) if we are purchasing ensure the purchase amount is not more than number of avalible shares in open market
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def sufficient_balance_validator(balance : float, shares_requested : tuple[str, int], purchase : bool) -> bool:
        # TODO: get price of stock from api
        # TODO: Validate that the user has sufficient balance for the requested stock and amount
        # TODO: if user is selling we return true by default
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def fund_validator(balance : float, funds_request : float) -> bool:
        # TODO: validate that the funds are positive and reasonable within discrecion
        pass