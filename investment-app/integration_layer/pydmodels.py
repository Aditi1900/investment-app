from pydantic import BaseModel


class LogoutRequest(BaseModel):
    session_id: str


class CredsRequest(BaseModel):
    login: str
    password: str


class FundsRequest(BaseModel):
    session_id: str
    funds_requested: float


class PortfolioRequest(BaseModel):
    session_id: str
    name: str


class TransactionRequest(BaseModel):
    session_id: str
    portfolio_name: str
    ticker: str
    quantity: int


class StockData(BaseModel):
    ticker: str
    quantity: int


class PortfolioData(BaseModel):
    name: str
    stocks: dict[str, StockData]

    @classmethod
    def convert(cls, portfolio):
        
        stocks = {}

        for ticker, stock in portfolio.stocks.items():
            stocks[ticker] = StockData(ticker = ticker, quantity = stock.quantity)

        return cls(name = portfolio.name, stocks = stocks)
       

class UserData(BaseModel):
    login: str
    balance: float
    portfolios: dict[str, PortfolioData]

    @classmethod
    def convert(cls, user):

        portfolios = {}

        for name, portfolio in user.portfolios.items():
            portfolios[name] = PortfolioData.convert(portfolio)
        
        return cls(login = user.login, balance = user.balance, portfolios = portfolios)