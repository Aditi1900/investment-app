import sys

from collections import defaultdict
from common.entropy import inject_volatility
from common.errors import DatabaseError, ServiceError
from common.security import secure_creds
from integration_layer import ExternalApi as eapi
from domain_models import User, Portfolio, Stock


# PURPOSE:
#   -Service provides a routing/serving, and memory populator abstraction
#   -Decouples business logic from the database and interface layers
class Service:
    def __init__(self, database):
        self.db = database
    

    # INPUT: 
    #   -credentials(tuple[str,str]); user login and password
    # OUTPUT: None
    # PRECONDITION:
    #   -credentials; login and password are non-empty strings, see Validator.account_validator() POSTCONDITION
    # POSTCONDITION: 
    #   -database; see Database.insert_user() POSTCONDITION
    # RAISES: 
    #   -ServiceError; database call fails
    def create_account(self, credentials : tuple[str, str]) -> None:
        credentials = secure_creds(credentials)

        try:
        # TODO: Add user to the database   
            self.db.insert_user(credentials)
        except DatabaseError as e:
            raise ServiceError("Failed to create account") from e


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -user(User); populated account for the given login
    # PRECONDITION:
    #   -login; a user with this login exists in the database
    # POSTCONDITION: 
    #   -user; populated with id, login, balance and all portfolios and respective stocks
    # RAISES:
    #   -ServiceError; database call fails
    def find_account(self, login : str) -> User:
        # TODO: Create user object
        try:
            user = User()
        # TODO: Populate user object
            self.populate_user_account(user, login)
            return user
        except DatabaseError as e:
            raise ServiceError("Failed to find account") from e


    # INPUT:
    #   -user_account(User); current user account
    #   -funds_request(float); amount of money to add to balance 
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -funds_request; > 0
    # POSTCONDITION: 
    #   -database; see Database.update_funds() POSTCONDITION
    #   -user_account; funds are added to account
    # RAISES:
    #   -ServiceError; database call fails
    def fund_account(self, user_account : User, funds_request : float) -> None:
        try:
        #TODO: update database funds
            self.db.update_funds(user_account.id, funds_request)
        except DatabaseError as e:
            raise ServiceError("Failed to update funds") from e

        user_account.add_funds(funds_request)
        

    # INPUT:  -----------------------------------------------------
    #   -user_account(User); current user account
    #   -portfolio_name(str); name of portfolio to create
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio_name; see Validator.portfolio_validator() POSTCONDITION
    # POSTCONDITION: 
    #   -database; see Database.insert_portfolio() POSTCONDITION
    #   -user_account; empty portfolio with portfolio_name is added to account
    # RAISES:
    #   -ServiceError; database call fails
    def create_portfolio(self, user_account : User, portfolio_name : str) -> None:
        try:
            p_id = self.db.insert_portfolio(user_account.id, portfolio_name)
        except DatabaseError as e:
            raise ServiceError("Failed to create portfolio") from e

        # TODO: add new empty portfolio to user_account object
        user_account.add_portfolio(portfolio_name)
        user_account.portfolios[portfolio_name].id = p_id


    # INPUT:
    #   -user_account(User); current user account
    #   -portfolio_name(str); name of portfolio to remove
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio_name; see Validator.portfolio_validator() POSTCONDITION
    # POSTCONDITION:
    #   -database; see Database.delete_portfolio() POSTCONDITION
    #   -user_account; portfolio is removed from in memory account
    # RAISES:
    #   -ServiceError; database call fails
    def remove_portfolio(self, user_account : User, portfolio_name : str) -> None:
        try:
        #TODO: call remove function for removing portfolio from database
            portfolio = user_account.portfolios[portfolio_name]
            self.db.delete_portfolio(portfolio.id)
        except DatabaseError as e:
            raise ServiceError("Failed to remove portfolio") from e

        user_account.remove_portfolio(portfolio_name)


    # INPUT: 
    #   -user_account(User); current user account
    #   -portfolio(Portfolio); some portfolio belonging to current user
    #   -shares_request(tuple[str,int]); requested stock ticker and quantity
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio; portfolio is up to date
    #   -shares_request; see Validator.shares_request_validator() POSTCONDITION
    # POSTCONDITION:
    #   -database; if ticker exists in portfolio see Database.update_stock(), else see Database.insert_stock() POSTCONDITION
    #   -user_account; balance is decremented based on purchase cost
    #   -portfolio; stock with matching ticker is added with quantity or updated
    # RAISES:
    #   -ServiceError; database call fails
    def execute_buy(self, user_account : User, portfolio : Portfolio, shares_request : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: subtract funds from user account
        
        ticker, quantity = shares_request

        price = eapi.get_stock_price(ticker)
        total_cost = price * quantity

        

        s_id = None

        try:
            self.db.update_funds(user_account.id, -total_cost)
            user_account.sub_funds(total_cost)

            if portfolio.has_stock(ticker):
                # TODO: update the database
                stock = portfolio.stocks[ticker]
                self.db.update_stock(stock.id, quantity)
            else:
                 s_id = self.db.insert_stock(portfolio.id, shares_request)
        except DatabaseError as e:
            raise ServiceError("Failed to execute buy") from e

        portfolio.buy_shares(shares_request)

        if s_id is not None:
            portfolio.stocks[ticker].id = s_id
        

    # INPUT: 
    #   -user_account(User); current user account
    #   -portfolio(Portfolio); some portfolio belonging to current user
    #   -shares_request(tuple[str,int]); requested stock ticker and quantity
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio; portfolio is up to date
    #   -shares_request; see Validator.shares_request_validator() POSTCONDITION
    # POSTCONDITION:
    #   -database; if quantity equals current holdings see Database.delete_stock(), else see Database.update_stock() POSTCONDITION
    #   -user_account; balance is incremented by sale value
    #   -portfolio; stock with matching ticker is updated or removed
    # RAISES:
    #   -ServiceError; database call fails
    def execute_sell(self, user_account : User, portfolio : Portfolio, shares_request : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: add funds to user account
        
        ticker, quantity = shares_request

        price = eapi.get_stock_price(ticker)
        total_value = price * quantity

        

        try:
            
            self.db.update_funds(user_account.id, total_value)
            user_account.add_funds(total_value)

            stock = portfolio.stocks[ticker]

            if portfolio.has_stock(ticker) and quantity == portfolio.stocks[ticker].quantity:
                # TODO: remove from the database
                self.db.delete_stock(stock.id)
            else:
                # TODO: update the database
                self.db.update_stock(stock.id, -quantity)
        except DatabaseError as e:
            raise ServiceError("Failed to execute sell") from e

        portfolio.sell_shares(shares_request)


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -user_dat(tuple); user id, login, password, balance
    # PRECONDITION: None
    # POSTCONDITION:
    #   -user_dat; user information provided if login exists in database, None otherwise
    # RAISES:
    #   -ServiceError; database call fails
    def identify_user(self, login : str) -> int:
        try:
            user_dat = self.db.pull_user(login)
        except DatabaseError as e:
            raise ServiceError("Failed to match credentials") from e

        return user_dat


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -user_password(str | None); stored password for given login
    # PRECONDITION: None
    # POSTCONDITION:
    #   -user_password; user password provided if login exists in database, None otherwise
    # RAISES:
    #   -ServiceError; propagated from identify_user()
    def resolve_password(self, login : str) -> str | None:
        user_password = None
        user_dat = self.identify_user(login)

        if user_dat is not None:
            user_password = user_dat[2]
           
        return user_password


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -u_id(int | None); stored user id for given login
    # PRECONDITION: None
    # POSTCONDITION:
    #   -u_id; user id provided if login exists in database, None otherwise
    # RAISES:
    #   -ServiceError; propagated from identify_user()
    def resolve_uid(self, login : str) -> int | None:
        u_id = None
        user_dat = self.identify_user(login)

        if user_dat is not None:
            u_id = user_dat[0]
            
        return u_id

    
    # INPUT:
    #   -portfolio(Portfolio); a user portfolio
    # OUTPUT:
    #   -packaged_data(list[dict[str,str|int]]); explicit labeler for each stock pair "ticker", "value" labels  
    # PRECONDITION: None
    # POSTCONDITION:
    #   -packaged_data; represents a labeled set of all stocks in portfolio
    # RAISES: None
    def package_portfolio_data(self, portfolio : Portfolio) -> list[dict[str, str | int]]:
        packaged_data = []
        total = 0

        for stock in portfolio.stocks.values():
            price = eapi.get_stock_price(stock.ticker)
            ticker, quantity = stock.ticker, stock.quantity

            value = quantity*price + inject_volatility(price)
            total += value
            packaged_data.append({"ticker": ticker, "value": value, "label": f"{ticker} (${value:,.2f})"})

        packaged_data.append(f"${total:,.2f}")

        return packaged_data


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -stored_user(tuple); user id, login, balance
    #   -stored_portfolios(list[tuple]); all user portfolios listed as portfolio id, name
    #   -stored_stocks(list[tuple]); all user stocks listed as portfolio id, stock id, ticker, quantity
    # PRECONDITION:
    #   -login; a user with this login exists in the database
    # POSTCONDITION:
    #   -stored_user; see Database.pull_user() POSTCONDITION
    #   -stored_portfolios; see Database.pull_portfolios() POSTCONDITION
    #   -stored_stocks; see Database.pull_stocks() POSTCONDITION
    # RAISES: None
    def retrieve_stored_data(self, login : str) -> tuple[tuple, list[tuple], list[tuple]]:
        stored_user = self.db.pull_user(login)
        stored_portfolios = self.db.pull_portfolios(stored_user[0])
        stored_stocks = self.db.pull_stocks(stored_user[0])

        return stored_user, stored_portfolios, stored_stocks


    # INPUT:
    #   -user_account(User); current user account
    #   -login(str); user login
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; is empty
    #   -login; a user with this login exists in the database
    # POSTCONDITION:
    #   -user_account; populated with id, login, balance, all portfolios and their stocks from database
    # RAISES: None
    def populate_user_account(self, user_account : User, login : str) -> None:
        stored_user, stored_portfolios, stored_stocks = self.retrieve_stored_data(login)

        user_account.id = stored_user[0]
        user_account.login = stored_user[1]
        user_account.balance = stored_user[3]

        self.populate_user_portfolios(user_account.portfolios, stored_portfolios, stored_stocks)
        

    # INPUT:
    #   -stored_stocks(list[tuple]); all user stocks listed as portfolio id, stock id, ticker, quantity
    # OUTPUT:
    #   -portfolio_assignments(dict[int, list[tuple]]); list of stock data keyed to specific portfolio id
    # PRECONDITION:
    #   -stored_stocks; see Database.pull_stocks() POSTCONDITION
    # POSTCONDITION:
    #   -portfolio_assignments; each portfolio id maps to its list of stock tuples
    # RAISES: None
    def assign_portfolio_allocations(self, stored_stocks : list[tuple]) -> dict[int, list[tuple]]:
        portfolio_assignments = defaultdict(list)
        for stock in stored_stocks:
            p_id = stock[0]
            portfolio_assignments[p_id].append(stock[1:])

        return portfolio_assignments


    # INPUT:
    #   -user_portfolios(dict[str,Portfolio]); user portfolios keyed by portfolio name
    #   -stored_portfolios(list[tuple]); all user portfolios listed as portfolio id, name 
    #   -stored_stocks(list[tuple]); all user stocks listed as portfolio id, stock id, ticker, quantity
    # OUTPUT: None
    # PRECONDITION:
    #   -user_portfolios; is empty
    #   -stored_portfolios; see Database.pull_portfolios() POSTCONDITION
    #   -stored_stocks; see Database.pull_stocks() POSTCONDITION
    # POSTCONDITION:
    #   -user_portfolios; populated with all portfolios and their respective stocks
    # RAISES: None
    def populate_user_portfolios(self, user_portfolios : dict[str, Portfolio], stored_portfolios : list[tuple], stored_stocks : list[tuple]) -> None:
        stored_stocks = self.assign_portfolio_allocations(stored_stocks)

        for portfolio in stored_portfolios:

            p_id = portfolio[0]
            p_name = portfolio[1]

            user_portfolios[p_name] = Portfolio(id=p_id,name=p_name)

            self.populate_portfolio_stocks(user_portfolios[p_name].stocks, stored_stocks.get(p_id, []))
    

    # INPUT:
    #   -portfolio_stocks(dict[str,Stock]); a users portfolio stocks keyed by ticker 
    #   -stored_portfolio_stocks(list[tuple]); specific portfolios stock list
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_stocks; is empty
    #   -stored_portfolio_stocks; contains all stocks for given portfolio
    # POSTCONDITION:
    #   -portfolio_stocks; populated with all stocks for the given portfolio
    # RAISES: None
    def populate_portfolio_stocks(self, portfolio_stocks : dict[str, Stock], stored_portfolio_stocks : list[tuple]) -> None:

        for stock in stored_portfolio_stocks:

            s_id = stock[0]
            s_ticker = stock[1]
            s_quantity = stock[2]

            portfolio_stocks[s_ticker] = Stock(id=s_id, ticker=s_ticker, quantity=s_quantity)


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION: None
    # POSTCONDITION: None
    #   -execution; program execution is terminated
    # RAISES:   
    #   -SystemExit; always raised on call
    @staticmethod
    def exit_app() -> None:
        sys.exit(0)