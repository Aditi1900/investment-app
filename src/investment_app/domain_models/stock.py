# PURPOSE:
#   -Stock provides a stock holding abstraction
#   -encapsulates data related to stock and provides methods of modifying it 
class Stock:
    def __init__(self, id=None, *, ticker, quantity):
        self.id = id
        self.ticker = ticker
        self.quantity = quantity


    # INPUT:
    #   -inc_amt(int); an amount of stock we want to increase
    # OUTPUT: None
    # PRECONDITION:
    #   -inc_amt; > 0
    # POSTCONDITION:
    #   -self.quantity; incremented by inc_amt
    # RAISES: None
    def increment_quantity(self, inc_amt : int) -> None:
        self.quantity += inc_amt


    # INPUT: 
    #   -dec_amt(int); an amount of stock we want to decrease
    # OUTPUT: None
    # PRECONDITION:
    #   -dec_amt; quantity >= dec_amt > 0
    # POSTCONDITION:
    #   -self.quantity; decremented by dec_amt
    # RAISES: None
    def decrement_quantity(self, dec_amt : int) -> None:
        self.quantity -= dec_amt