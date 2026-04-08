from enum import verify
import re
import bcrypt
from typing import NamedTuple

from integration_layer import ExternalApi as eapi

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
    #   -new; is True or False
    # POSTCONDITION:
    #   -Result; True if credentials match stored record, or password >= 6 chars (new)
    # RAISES: None
    def account_validator(self, credentials : tuple[str, str], new : bool) -> Result:

        def password_match(plain : str, hashed : str) -> bool:
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

        login, password = credentials
        
        if login == '' and password != '' and not password.isspace():
            return Result(False, "No username entered.\n")

        if login != '' and (password == '' or password.isspace()):
            return Result(False, "No password entered.\n")

        if login == '' and (password == '' or password.isspace()):
            return Result(False, "No credentials entered.\n")
        
        stored_password = self.serv.resolve_password(login)
        account_exists = stored_password is not None

        if new and account_exists:
            return Result(False, "An account with this username already exists.\n")

        if new and not account_exists and len(password) < 6:
            return Result(False, "Password must be six characters or more.\n")
        
        if not new and account_exists and not password_match(password, stored_password):
            return Result(False, "Invalid password.\n")

        if not new and not account_exists:
            return Result(False, "No account exists with entered username.\n")

        if new:
            return Result(True, f"{login} has successfully created a new account.\n")
        else:
            return Result(True, f"{login} has successfully logged in.\n")



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
    #   -Result; True if name is non-empty and not taken (create), or exists in account and is empty
    # RAISES: None
    @staticmethod
    def portfolio_validator(user_account, portfolio_name : str, create : bool) -> Result:
        # TODO: Validate that portfolio_name doesnt already exist
        # TODO: Add any other validation you want, AKA empty name insert
        # TODO: ensure creation only is allowed when portfolio doesnt exist and removal is only allowed when it does

        in_account = portfolio_name in user_account.portfolios
        portfolio_empty = not user_account.portfolios[portfolio_name].stocks if in_account else False 


        if create and portfolio_name == '':
            return Result(False, "Portfolio name cannot be empty.\n")

        if create and in_account:
            return Result(False, "Portfolio with same name already exists.\n")
        
        if not create and not in_account:
           return Result(False, "Portfolio does not exist.\n")
        
        if not create and not portfolio_empty:
            return Result(False, "Portfolio needs to be liquidated before removal.\n")

        if create:
            return Result(True, f"Portfolio {portfolio_name} successfully created.\n")
        else:
            return Result(True, f"Portfolio {portfolio_name} successfully removed.\n")



    # INPUT:
    #   -portfolio(Portfolio); user portfolio to update
    #   -balance(float); users current balance
    #   -shares_request(tuple[str,int]); ticker and quantity of shares requested
    #   -purchase(bool); True if purchasing, False if selling
    # OUTPUT:
    #   -return(Result); validation result True or False with reason
    # PRECONDITION:
    #   -portfolio.stocks; accessable and current
    #   -balance; >= 0
    #   -purchase; is True or False
    # POSTCONDITION:
    #   -Result; True if all three sub-validations pass, False with first failing reason
    # RAISES: None
    @staticmethod
    def shares_request_validator(portfolio, shares_request : tuple[str,int], balance : float, purchase : bool):

        ticker, quantity = shares_request

        if quantity is None:
            return Result(False, "Quantity entered must be a valid number.\n")

        #Validate ticker
        if not re.fullmatch(r"[A-Z]{1,5}", ticker):
           return Result(False, "Ticker symbols must be capital and 1-5 characters.\n")
        
        if purchase and not eapi.does_ticker_exist(ticker):
           return Result(False, "This stock does not exist on the open market.\n")
        
        if not purchase and ticker not in portfolio.stocks:
            return Result(False, "You do not own this stock.\n")


        #Validate Quantity
        if quantity <= 0:
            return Result(False, "Requested quantity must be positive.\n")

        if purchase and eapi.get_float(ticker) < quantity:
           return Result(False, "Requested quantity exceeds available shares on open market.\n")
            
        if not purchase and portfolio.stocks[ticker].quantity < quantity:
            return Result(False, "You do not own enough shares to sell.\n")


        #Validate Balance
        if purchase: 
            price = eapi.get_price(ticker)
            total_cost = price * quantity

            if balance < total_cost:
                return Result(False, "Shares requested exceed current balance.\n")

        if purchase:
            return Result(True, f"{quantity} shares of {ticker} successfully purchased.\n")
        else:
            return Result(True, f"{quantity} shares of {ticker} successfully sold.\n")


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
        if funds_request is None:
            return Result(False, "Funds requested must be a valid number.\n")
        # ensures funds requested are in valid range zero - one-million
        if funds_request >= 1_000_000 or funds_request <= 0:
            return Result(False, "Funds request must be between 1-999,999.\n")

        return Result(True, "Funds request was successful.\n")


   

