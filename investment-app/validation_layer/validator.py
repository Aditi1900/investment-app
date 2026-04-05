import re
from typing import NamedTuple

from integration_layer import ExternalApi as eapi, PortfolioData, PortfolioRequest

# PURPOSE: 
#   -Result provides description abstraction
#   -Ensures that a validator can return specific error message and a bool
class Result(NamedTuple):
    valid: bool
    reason: str = ""


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
    #   -return(Result); account validation result True or False with description
    # PRECONDITION:
    #   -credentials; login and password are non-empty strings
    #   -new; is True or False
    # POSTCONDITION:
    #   -Result; True if credentials match stored record, or password >= 6 chars (new)
    # RAISES: None
    def account_validator(self, credentials : tuple[str, str], new : bool) -> Result:
        # TODO: Validate account credentials using service method
        # TODO: Add any other validation you want, if you want to enforce certain additional constraints
        login, password = credentials
        
        if login == '' and password != '':
            return Result(False, "No username entered.")

        if login != '' and password == '':
            return Result(False, "No password entered.")

        if login == '' and password == '':
            return Result(False, "No credentials entered.")
        
        stored_password = self.serv.resolve_password(login)
        account_exists = stored_password is not None

        if account_exists and password != stored_password:
            return Result(False, "Invalid password.")

        if new and account_exists:
            return Result(False, "An account with this username already exists.")

        if new and not account_exists and len(password) < 6:
            return Result(False, "Password must be six characters or more.")
        
        if not new and not account_exists:
            return Result(False, "No account exists with entered username.")

        return Result(True)




    # INPUT:
    #   -user_account(User); current user account 
    #   -portfolio_name(str); requested name of portfolio
    #   -create(bool); True if portfolio is being created, False if being accessed
    # OUTPUT:
    #   -return(Result); portfolio validation result True or False with reason
    # PRECONDITION:
    #   -user_account.portfolios; accessible and current
    #   -create; is True or False
    # POSTCONDITION:
    #   -Result; True if name is non-empty and not taken (create), or exists in account
    # RAISES: None
    @staticmethod
    def portfolio_validator(user_account, portfolio_name : str, create : bool) -> Result:
        # TODO: Validate that portfolio_name doesnt already exist
        # TODO: Add any other validation you want, AKA empty name insert
        # TODO: ensure creation only is allowed when portfolio doesnt exist and removal is only allowed when it does

        in_account = portfolio_name in user_account.portfolios

        if create and portfolio_name == '':
            return Result(False, "Portfolio name cannot be empty.")

        if create and in_account:
            return Result(False, "Portfolio with same name already exists.")
        
        if not create and not in_account:
           return Result(False, "Portfolio does not exist.")

        return Result(True)


    # INPUT:
    #   -portfolio(Portfolio); user portfolio to update
    #   -ticker(str); requested stock ticker symbol
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -return(Result); stock ticker validation result True or False with reason
    # PRECONDITION:
    #   -portfolio.stocks; accessible and current
    #   -purchase; is True or False
    # POSTCONDITION:
    #   -Result; True if format matches [A-Z]{1,5} and exists in yfinance (purchase), or exists in portfolio (sell)
    # RAISES: None
    @staticmethod
    def stock_ticker_validator(portfolio, ticker : str, purchase : bool) -> Result:
        # TODO: Validate ticker symbol format with regex
        # TODO: identify if we are purchasing a stock or not
        # TODO: if stock is not being purchased check if it exists in the portfolio
        # TODO: if stock is being purchased find out if it exists in yfinance
        # TODO: if ticker doesnt exist in portfolio and we arent purchasing return false
        ticker = ticker.strip()
        
        # checking if format is valid
        correct_format = re.fullmatch(r"[A-Z]{1,5}", ticker)

        if not correct_format:
           return Result(False, "Ticker symbols must be capital and 1-5 characters.")
        
        if purchase and not eapi.does_ticker_exist(ticker):
           return Result(False, "This stock does not exist on the open market.")
        
        if not purchase and ticker not in portfolio.stocks:
            return Result(False, "You do not own this stock.")
            
        return Result(True)


    # INPUT:
    #   -portfolio(Portfolio); user portfolio to update
    #   -shares_requested(tuple[str,int]); ticker and quantity of shares requested
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -return(Result); stock quantity validation result True or False with reason
    # PRECONDITION:
    #   -shares_requested; ticker is valid, see stock_ticker_validator() POSTCONDITION
    #   -quantity; > 0
    #   -purchase; is True or False
    # POSTCONDITION:
    #   -Result; True if quantity > 0 and does not exceed float shares (purchase), or current holdings (sell)
    # RAISES: None
    @staticmethod
    def stock_quantity_validator(portfolio, shares_requested : tuple[str, int], purchase : bool) -> Result:
        # TODO: If we are not purchasing check if portfolio has enough shares of stock
        # TODO: (optional) if we are purchasing ensure the purchase amount is not more than number of available shares in open market
        
        ticker, quantity = shares_requested

        if quantity <= 0:
            return Result(False, "Requested quantity must be positive.")

        if purchase and eapi.get_float(ticker) < quantity:
           return Result(False, "Requested quantity exceeds available shares on open market.")
            
        if not purchase and portfolio.stocks[ticker].quantity < quantity:
            return Result(False, "You do not own enough shares to sell.")
        
        return Result(True)


    # INPUT:
    #   -balance(float); users current balance
    #   -shares_requested(tuple[str,int]); ticker and quantity of shares requested
    #   -purchase(bool); True if a stock is being purchased, False if being sold
    # OUTPUT:
    #   -return(Result); user balance validator result True or False with reason
    # PRECONDITION:
    #   -balance; >= 0
    #   -shares_requested; ticker and quantity are valid, see stock_ticker_validator() & stock_quantity_validator() POSTCONDITIONS
    #   -purchase; is True or False
    # POSTCONDITION:
    #   -Result; True if balance >= price * quantity (purchase), or True unconditionally (sell)
    # RAISES: None
    @staticmethod
    def sufficient_balance_validator(balance : float, shares_requested : tuple[str, int], purchase : bool) -> Result:
        # TODO: get price of stock from api
        # TODO: Validate that the user has sufficient balance for the requested stock and amount
        # TODO: if user is selling we return true by default
        
        ticker, quantity = shares_requested

        # to get stock price from api
        if purchase: 
            price = eapi.get_price(ticker)
            total_cost = price * quantity

            if balance < total_cost:
                return Result(False, "Shares requested exceed current balance.")
            
        return Result(True)


    # INPUT:
    #   -funds_request(float); requested funds to add
    # OUTPUT:
    #   -return(Result); requested funds validator result True or False with reason
    # PRECONDITION:
    #   -funds_request; is a float
    # POSTCONDITION:
    #   -Result; True if 0 < funds_request < 1,000,000
    # RAISES: None
    @staticmethod
    def fund_validator(funds_request : float) -> Result:
        # TODO: validate that the funds are positive and reasonable within discrecion
    
        # ensures funds requested are in valid range zero - one-million
        if funds_request >= 1_000_000 or funds_request <= 0:
            return Result(False, "Funds request must be between 1-999,999.")

        return Result(True)


   

