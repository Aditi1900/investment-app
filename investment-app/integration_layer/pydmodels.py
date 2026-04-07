from pydantic import BaseModel


# PURPOSE:
#   -LogoutRequest provides a deserializable abstraction for logout data
#   -defines the expected JSON body shape for the /logout endpoint
class LogoutRequest(BaseModel):
    session_id: str


# PURPOSE:
#   -CredsRequest provides a deserializable abstraction for credentials
#   -defines the expected JSON body shape for the /register and /login endpoints
class CredsRequest(BaseModel):
    login: str
    password: str


# PURPOSE:
#   -FundsRequest provides a deserializable abstraction for funds deposit data
#   -defines the expected JSON body shape for the /fund endpoint
class FundsRequest(BaseModel):
    session_id: str
    funds_requested: float


# PURPOSE:
#   -PortfolioRequest provides a deserializable abstraction for portfolio data
#   -defines the expected JSON body shape for the /portfolio/create and /portfolio/remove endpoints 
class PortfolioRequest(BaseModel):
    session_id: str
    name: str


# PURPOSE:
#   -TransactionRequest provides a deserializable abstraction for transaction data
#   -defines the expected JSON body shape for the /buy and /sell endpoints 
class TransactionRequest(BaseModel):
    session_id: str
    portfolio_name: str
    ticker: str
    quantity: int


# PURPOSE:
#   -StockData provides a serializable abstraction for a Stock object
#   -defines the JSON response body for a Stock
class StockData(BaseModel):
    ticker: str
    quantity: int


# PURPOSE:
#   -PortfolioData provides a serializable abstraction for a Portfolio object
#   -defines the JSON response body for a Portfolio 
class PortfolioData(BaseModel):
    name: str
    stocks: dict[str, StockData]


    # INPUT:
    #   -portfolio(Portfolio); a user portfolio
    # OUTPUT:
    #   -portfolio_data(PortfolioData); an object representing serializable data of portfolio
    # PRECONDITION:
    #   -portfolio; fully populated and up to date
    # POSTCONDITION:
    #   -portfolio_data; properly represents the JSON response body of a portfolio
    # RAISES: None
    @classmethod
    def convert(cls, portfolio):
        
        stocks = {}

        for ticker, stock in portfolio.stocks.items():
            stocks[ticker] = StockData(ticker = ticker, quantity = stock.quantity)

        portfolio_data = cls(name = portfolio.name, stocks = stocks)

        return portfolio_data
       

# PURPOSE:
#   -UserData provides a serializable abstraction for a User object
#   -defines the JSON response body for a User
class UserData(BaseModel):
    login: str
    balance: float
    portfolios: dict[str, PortfolioData]


    # INPUT:
    #   -user(User); current user account
    # OUTPUT:
    #   -user_data(UserData); an object representing serializable data of user
    # PRECONDITION:
    #   -user; fully populated and up to date
    # POSTCONDITION:
    #   -user_data; properly represents the JSON response body of a user
    # RAISES: None
    @classmethod
    def convert(cls, user):

        portfolios = {}

        for name, portfolio in user.portfolios.items():
            portfolios[name] = PortfolioData.convert(portfolio)
        
        user_data = cls(login = user.login, balance = user.balance, portfolios = portfolios)

        return user_data