from stock import Stock

class Portfolio:
    def __init__(self, name, stocks : list[Stock]):
        self.name = name
        self.stocks = stocks