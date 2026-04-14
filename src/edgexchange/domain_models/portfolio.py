from .stock import Stock


# PURPOSE:
#   -Portfolio provides a portfolio abstraction
#   -encapsulates data related to a portfolio and provides methods for manipulating or evaluating a portfolio
class Portfolio:
    def __init__(self, id=None, *, name, stocks: dict[str, Stock] = None):
        self.id = id
        self.name = name
        self.stocks = stocks if stocks is not None else {}


    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -exists(bool); whether ticker is held in portfolio
    # PRECONDITION: None
    # POSTCONDITION:
    #   -exists; True if ticker held, False otherwise
    # RAISES: None
    def has_stock(self, ticker : str) -> bool:
        exists = ticker in self.stocks
        return exists


    # INPUT:
    #   -shares_requested(tuple[str,int]); a request for a ticker and quantity of stocks
    #   -s_id(int); an existing stock id
    # OUTPUT: None
    # PRECONDITION:
    #   -s_id; is None or holds existing stock id
    #   -ticker; exists in open market
    #   -quantity; > 0
    # POSTCONDITION:
    #   -self.stocks; ticker quantity incremented if held, otherwise new Stock added
    # RAISES: None
    def buy_shares(self, shares_requested : tuple[str, int], s_id : int) -> None:

        t, q = shares_requested

        if self.has_stock(t):
            self.stocks[t].increment_quantity(q)
        else:
            self.stocks[t] = Stock(id=s_id, ticker=t, quantity=q)


    # INPUT:
    #   -shares_requested(tuple[str,int]); a request for a ticker and quantity of stocks
    # OUTPUT: None
    # PRECONDITION:
    #   -ticker; exists in self.stocks
    #   -quantity; current holdings >= quantity > 0
    # POSTCONDITION:
    #   -self.stocks; ticker quantity decremented, and removed if quantity reaches 0
    # RAISES: None
    def sell_shares(self, shares_requested : tuple[str, int]) -> None:

        t, q = shares_requested

        self.stocks[t].decrement_quantity(q)

        if self.stocks[t].quantity == 0:
            del self.stocks[t]