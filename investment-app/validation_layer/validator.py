from integration_layer import Api as api


# PURPOSE: 
#   -Validator provides validation abstraction
#   -Ensures all user input meets constraints before reaching lower layers
class Validator:
    def __init__(self, service):
        self.serv = service


    # INPUT:
    #   -credentials(tuple[str,str]); user login and password
    #   -new(bool); True if creating a new account, False if logging in
    # OUTPUT:
    #   -valid(bool); account validation result True or False
    # PRECONDITION:
    #   -new; is not None
    # POSTCONDITION:
    #   -valid; True if credentials meet all constraints, False otherwise
    # RAISES: None
    def account_validator(self, credentials : tuple[str, str], new : bool) -> bool:
        # TODO: Validate account credentials using service method
        # TODO: Add any other validation you want, if you want to enforce certain additional constraints
        pass

     
    # INPUT:
    #   -user_account(User); current user account 
    #   -portfolio_name(str); requested name of portfolio
    #   -create(bool); True if portfolio is being created, False if being accessed
    # OUTPUT:
    #   -valid(bool); portfolio validation result True or False
    # PRECONDITION:
    #   -user_account; user account is fully populated and up to date
    #   -create; is not None
    # POSTCONDITION:
    #   -valid; True if portfolio name exists or is available and meets all constraints, False otherwise
    # RAISES: None
    @staticmethod
    def portfolio_validator(user_account, portfolio_name : str, create : bool) -> bool:
        # TODO: Validate that portfolio_name doesnt already exist
        # TODO: Add any other validation you want, AKA empty name insert
        # TODO: ensure creation only is allowed when portfolio doesnt exist and removal is only allowed when it does
        pass


    # INPUT:
    #   -portfolio(Portfolio); user portfolio to update
    #   -ticker(str); requested stock ticker symbol
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -valid(bool); stock ticker validation result True or False
    # PRECONDITION:
    #   -portfolio; user portfolio is fully populated and up to date
    #   -purchase; is not None
    # POSTCONDITION:
    #   -valid; True if ticker meets all constraints for given purchase state, False otherwise 
    # RAISES: None
    @staticmethod
    def stock_ticker_validator(portfolio, ticker : str, purchase : bool) -> bool:
        # TODO: Validate ticker symbol format with regex
        # TODO: identify if we are purchasing a stock or not
        # TODO: if stock is not being purchased check if it exists in the portfolio
        # TODO: if stock is being purchased find out if it exists in yfinance
        # TODO: if ticker doesnt exist in portfolio and we arent purchasing return false
        pass


    # INPUT:
    #   -portfolio(Portfolio); user portfolio to update
    #   -shares_requested(tuple[str,int]); ticker and quantity of shares requested
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -valid(bool); stock quantity validation result True or False
    # PRECONDITION:
    #   -shares_requested; ticker of requested shares is valid, see Validator.stock_ticker_validator() POSTCONDITION
    #   -portfolio; user portfolio is fully populated and up to date
    #   -purchase; is not None
    # POSTCONDITION:
    #   -valid; True if quantity meets all constraints for given purchase state, False otherwise
    # RAISES: None
    @staticmethod
    def stock_quantity_validator(portfolio, shares_requested : tuple[str, int], purchase : bool) -> bool:
        # TODO: If we are not purchasing check if portfolio has enough shares of stock
        # TODO: (optional) if we are purchasing ensure the purchase amount is not more than number of avalible shares in open market
        pass


    # INPUT:
    #   -balance(float); users current balance
    #   -shares_requested(tuple[str,int]); ticker and quantity of shares requested
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -valid(bool); user balance validator result True or False
    # PRECONDITION:
    #   -balance; user balance >= 0
    #   -shares_requested; requested shares are valid, see Validator.stock_ticker_validator() & Validator.stock_quantity_validator() POSTCONDITIONS
    #   -purchase; is not None
    # POSTCONDITION:
    #   -valid; True if user has sufficient balance, False otherwise
    # RAISES: None
    @staticmethod
    def sufficient_balance_validator(balance : float, shares_requested : tuple[str, int], purchase : bool) -> bool:
        # TODO: get price of stock from api
        # TODO: Validate that the user has sufficient balance for the requested stock and amount
        # TODO: if user is selling we return true by default
        pass


    # INPUT:
    #   -balance(float); users current balance
    #   -funds_request(float); requested funds to add
    # OUTPUT:
    #   -valid(bool); requested funds validator result True or False
    # PRECONDITION:
    #   -balance; user balance >= 0
    # POSTCONDITION:
    #   -valid; True if funds_request > 0 and meets all constraints, False otherwise
    # RAISES: None
    @staticmethod
    def fund_validator(balance : float, funds_request : float) -> bool:
        # TODO: validate that the funds are positive and reasonable within discrecion
        pass