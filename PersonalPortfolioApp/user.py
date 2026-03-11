from portfolio import Portfolio

class User:
    def __init__(self, login, password, balance, portfolios : list[Portfolio]):
        self.login = login
        self.password = password
        self.balance = balance
        self.portfolios = portfolios