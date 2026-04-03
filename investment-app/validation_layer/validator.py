import re

from integration_layer import ExternalApi as eapi, PortfolioData, PortfolioRequest


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
        valid = False
        login, password = credentials
        
        if login == '' or password == '':
            return valid
        
        valid = self.serv.credentials_match(credentials)

        if new:
            # password should be more than 6 chars in length
            valid = not valid and len(password) >= 6
        
        return valid


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

        valid = portfolio_name in user_account.portfolios

        if create:
            valid = (portfolio_name == '')

        return valid


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
        valid = False
        ticker = ticker.strip()
        
        # checking if format is valid
        valid = re.fullmatch(r"[A-Z]{1,5}", ticker)

        if purchase and valid:
           valid = eapi.does_ticker_exist(ticker)
           
        else:
            # if NOT purchasing ensure that ticker exists in portfolio
            valid = ticker in portfolio.stocks
            
        return valid


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
        
        ticker, quantity = shares_requested

        cur_quantity = portfolio.stocks[ticker].quantity

        # quantity must be positive
        valid = quantity > 0

        if purchase and valid:
            # validating that a user is not purchasing more in open market
            max_stocks = eapi.get_float(ticker)
            valid = max_stocks <= quantity
            
        elif valid:
            # if selling ensure enough shares exist
            valid = cur_quantity >= quantity
        
        return valid



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
        
        ticker, quantity = shares_requested

        # to get stock price from api
        if purchase: 
            price = eapi.get_price(ticker)

            # to ensure user has sufficient balance
            total_cost = price * quantity
            
            valid = (balance >= total_cost)
            
        else:
            valid = True
            
        return valid



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
    def fund_validator(funds_request : float) -> bool:
        # TODO: validate that the funds are positive and reasonable within discrecion
    
        # ensures funds requested are in valid range zero - one-million
        valid = (1_000_000 > funds_request > 0)

        return valid