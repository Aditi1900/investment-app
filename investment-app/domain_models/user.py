from threading import Lock
from .portfolio import Portfolio

# PURPOSE:
#   -User provides a user account abstraction
#   -encapsulates data related to a user account and methods to modify account values
class User:
    def __init__(self, id=None, *, login, balance, portfolios: dict[str, Portfolio] = None):
        self.id = id
        self.login = login
        self.balance = balance
        self.portfolios = portfolios if portfolios is not None else {}

        self.lock = Lock()


    # INPUT:
    #   -portfolio_name(str); a name for a portfolio
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_name; portfolio name is not in use by user and is not empty
    # POSTCONDITION:
    #   -User; a portfolio is added to the users portfolio collection with the input name
    # RAISES: None
    def add_portfolio(self, portfolio_name : str) -> None:
        self.portfolios[portfolio_name] = Portfolio(name = portfolio_name)


    # INPUT:
    #   -portfolio_name(str); a name of a portfolio
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_name; user has a portfolio with this name
    # POSTCONDITION:
    #   -User; portfolio with input name is deleted from user collection
    # RAISES: None
    def remove_portfolio(self, portfolio_name : str) -> None:
        del self.portfolios[portfolio_name]

    
    # INPUT:
    #   -funds_to_add(float); an amount of money
    # OUTPUT: None
    # PRECONDITION:
    #   -funds_to_add; >= 0
    # POSTCONDITION:
    #   -User; users balance is updated to reflect the added funds
    # RAISES: None
    def add_funds(self, funds_to_add : float) -> None:
        self.balance += funds_to_add


    # INPUT:
    #   -funds_to_sub(float); an amount of money
    # OUTPUT: None
    # PRECONDITION:
    #   -funds_to_sub; balance >= funds_to_sub >= 0 
    # POSTCONDITION:
    #   -User; users balance is updated to reflect the removed funds
    # RAISES: None
    def sub_funds(self, funds_to_sub : float) -> None:
        self.balance -= funds_to_sub






