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
    #   -portfolio_name; not empty and not already in self.portfolios
    # POSTCONDITION:
    #   -self.portfolios; new empty Portfolio keyed by portfolio_name
    # RAISES: None
    def add_portfolio(self, portfolio_name : str) -> None:
        self.portfolios[portfolio_name] = Portfolio(name = portfolio_name)


    # INPUT:
    #   -portfolio_name(str); a name of a portfolio
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_name; exists as a key in self.portfolios
    # POSTCONDITION:
    #   -self.portfolios; portfolio keyed by portfolio_name is removed
    # RAISES: None
    def remove_portfolio(self, portfolio_name : str) -> None:
        del self.portfolios[portfolio_name]


    # INPUT:
    #   -funds_to_add(float); an amount of money
    # OUTPUT: None
    # PRECONDITION:
    #   -funds_to_add; > 0
    # POSTCONDITION:
    #   -self.balance; incremented by funds_to_add
    # RAISES: None
    def add_funds(self, funds_to_add : float) -> None:
        self.balance += funds_to_add


    # INPUT:
    #   -funds_to_sub(float); an amount of money
    # OUTPUT: None
    # PRECONDITION:
    #   -funds_to_sub; balance >= funds_to_sub > 0
    # POSTCONDITION:
    #   -self.balance; decremented by funds_to_sub
    # RAISES: None
    def sub_funds(self, funds_to_sub : float) -> None:
        self.balance -= funds_to_sub