from .portfolio import Portfolio

# PURPOSE:
class User:

    def __init__(self, id=None, *, login, password, balance, portfolios: dict[str, Portfolio] = None):
        self.id = id
        self.login = login
        self.password = password
        self.balance = balance
        self.portfolios = portfolios if portfolios is not None else {}


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def add_portfolio(self, portfolioName):
        self.portfolios[portfolioName] = Portfolio(name = portfolioName)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def remove_portfolio(self, portfolioName):
        del self.portfolios[portfolioName]

    
    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def add_funds(self, funds_to_add):
        self.balance += funds_to_add


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def sub_funds(self, funds_to_sub):
        self.balance -= funds_to_sub






