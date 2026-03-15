from .stock import Stock

# PURPOSE:
class Portfolio:

    def __init__(self, id=None, *, name, stocks: dict[str, Stock] = None):
        self.id = id
        self.name = name
        self.stocks = stocks if stocks is not None else {}


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def portfolio_has_stock(self, ticker):
        return ticker in self.stocks


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def buy_shares(self, stock_dat):
        flag = ""

        t, q = stock_dat

        s_id = None

        if (self.portfolio_has_stock(t)):
            self.stocks[t].increment_quantity(q)
            s_id = self.stocks[t].id
        else:
            self.stocks[t] = Stock(ticker=t, quantity=q)
            flag = "new"

        return s_id, flag


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def sell_shares(self, stock_dat):
        flag = ""

        t, q = stock_dat

        s_id = self.stocks[t].id

        self.stocks[t].decrement_quantity(q)

        if (self.stocks[t].quantity == 0):
            del self.stocks[t]
            flag = "removed"

        return s_id, flag

