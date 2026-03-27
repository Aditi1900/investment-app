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
        return cls(

            name = portfolio.name,

            stocks = {
                ticker: StockData(ticker = ticker, quantity = qty)
                for ticker, qty in portfolio.stocks.items()
            }
        )
       

class UserData(BaseModel):
    login: str
    balance: float
    portfolios: dict[str, PortfolioData]

    @classmethod
    def convert(cls, user):
        return cls(

            login = user.login,

            balance = user.balance,

            portfolios = {
                name: PortfolioData.convert(portfolio)
                for name, portfolio in user.portfolios.items()
            }
        )