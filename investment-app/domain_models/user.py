from .portfolio import Portfolio

# PURPOSE:
class User:
    def __init__(self, id=None, *, login, balance, portfolios: dict[str, Portfolio] = None):
        self.id = id
        self.login = login
        self.balance = balance
        self.portfolios = portfolios if portfolios is not None else {}


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def add_portfolio(self, portfolio_name : str) -> None:
        self.portfolios[portfolio_name] = Portfolio(name = portfolio_name)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def remove_portfolio(self, portfolio_name : str) -> None:
        del self.portfolios[portfolio_name]

    
    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def add_funds(self, funds_to_add : float) -> None:
        self.balance += funds_to_add


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def sub_funds(self, funds_to_sub : float) -> None:
        self.balance -= funds_to_sub






