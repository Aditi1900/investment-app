from api import Api as api

class Validator:
    def __init__(self, service):
        self.serv = service
    
    def account_validator(self, credentials, isNew) -> bool:
        pass

    @staticmethod
    def portfolio_validator(userAccount, portfolioName) -> bool:
        pass
    @staticmethod
    def stock_ticker_validator(portfolio, ticker, isPurchase) -> bool:
        pass
    @staticmethod
    def stock_quantity_validator(portfolio, stock, isPurchase) -> bool:
        pass
    @staticmethod
    def sufficient_balance_validator(balance, stock, isPurchase) -> bool:
        pass