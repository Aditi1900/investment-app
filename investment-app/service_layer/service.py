import sys
from persistence_layer import DatabaseError
from collections import defaultdict
from domain_models import *

# PURPOSE: 
#   -ServiceError provides a central service error abstraction
#   -Allows for exceptions to be re-raised as a general errortype for this layer
class ServiceError(Exception):
    pass


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
    #   -credentials; see Validator.account_validator() POSTCONDITION
    # POSTCONDITION: 
    #   -db; see Database.insert_user() POSTCONDITION
    # RAISES: 
    #   -ServiceError; database call fails
    def create_account(self, credentials : tuple[str, str]) -> None:
        try:
        # TODO: Add user to the db
            pass
        except DatabaseError as e:
            raise ServiceError("Failed to create account") from e


    # INPUT:
    #   -login(str); user login
    # OUTPUT:
    #   -user(User); represents current user
    # PRECONDITION:
    #   -login; a user with this login exists in the database
    # POSTCONDITION: 
    #   -user; populated with id, login, balance and all portfolios and respective stocks
    # RAISES:
    #   -ServiceError; database call fails
    def find_account(self, login : str) -> User:
        # TODO: Create user object
        try:
        # TODO: Populate user object
            pass
        except DatabaseError as e:
            raise ServiceError("Failed to find account") from e


    # INPUT:
    #   -user_account(User); current user account
    #   -funds_request(float); amount of money to add to balance 
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -funds_request; funds requested are > 0
    # POSTCONDITION: 
    #   -db; see Database.update_funds() POSTCONDITION
    #   -user_account; funds are added to account
    # RAISES:
    #   -ServiceError; database call fails
    def fund_account(self, user_account : User, funds_request : float) -> None:
        try:
        #TODO: update db funds
            pass
        except DatabaseError as e:
            raise ServiceError("Failed to update funds") from e

        user_account.add_funds(funds_request)
        

    # INPUT:
    #   -user_account(User); current user account
    #   -portfolio_name(str); name of portfolio to create
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio_name; see Validator.portfolio_validator() POSTCONDITION
    # POSTCONDITION: 
    #   -db; see Database.insert_portfolio() POSTCONDITION
    #   -user_account; empty portfolio with portfolio_name is added to account
    # RAISES:
    #   -ServiceError; database call fails
    def create_portfolio(self, user_account : User, portfolio_name : str) -> None:
        try:

            p_id = self.db.insert_portfolio(user_account.id, portfolio_name)

        except DatabaseError as e:
            raise ServiceError("Failed to create portfolio") from e

        # TODO: add new empty portfolio to user_account object
        user_account.portfolios[portfolio_name].id = p_id


    # INPUT:
    #   -user_account(User); current user account
    #   -portfolio_name(str); name of portfolio to remove
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date
    #   -portfolio_name; see Validator.portfolio_validator() POSTCONDITION
    # POSTCONDITION:
    #   -db; see Database.delete_portfolio() POSTCONDITION
    #   -user_account; portfolio is removed from in memory account
    # RAISES:
    #   -ServiceError; database call fails
    def remove_portfolio(self, user_account : User, portfolio_name : str) -> None:
        try:
        #TODO: call remove function for removing portfolio from db
            pass
        except DatabaseError as e:
            raise ServiceError("Failed to remove portfolio") from e

        user_account.remove_portfolio(portfolio_name)


    # INPUT: 
    #   -user_account(User); current user account
    #   -portfolio(Portfolio); some portfolio belonging to current user
    #   -shares_requested(tuple[str,int]); requested stock ticker and quantity
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date in memory, and see Validator.sufficient_balance_validator() POSTCONDITION
    #   -portfolio; portfolio is up to date
    #   -shares_requested; see Validator.stock_ticker_validator() & Validator.stock_quantity_validator() POSTCONDITIONS
    # POSTCONDITION:
    #   -db; if portfolio already has the requested share see Database.update_stock(), else see Database.insert_stock() POSTCONDITION
    #   -user_account; balance is decremented based on purchase cost
    #   -portfolio; stock with matching ticker is added with quantity or updated
    # RAISES:
    #   -ServiceError; database call fails
    def execute_buy(self, user_account : User, portfolio : Portfolio, shares_requested : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: subtract funds from user account
        
        ticker, quantity = shares_requested

        s_id = None

        try:

            if portfolio.has_stock(ticker):
                # TODO: update the db
                pass
            else:
                 s_id = self.db.insert_stock(portfolio.id, shares_requested)
        
        except DatabaseError as e:
            raise ServiceError("Failed to execute buy") from e

        portfolio.buy_shares(shares_requested)

        if s_id != None:
            portfolio.stocks[ticker].id = s_id
        

    # INPUT: 
    #   -user_account(User); current user account
    #   -portfolio(Portfolio); some portfolio belonging to current user
    #   -shares_requested(tuple[str,int]); requested stock ticker and quantity
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; account info is up to date in memory
    #   -portfolio; portfolio is up to date
    #   -shares_requested; see Validator.stock_ticker_validator() & Validator.stock_quantity_validator() POSTCONDITIONS
    # POSTCONDITION:
    #   -db; if portfolio already has the requested share see Database.update_stock(), else see Database.delete_stock() POSTCONDITION
    #   -user_account; balance is incremented by sale value
    #   -portfolio; stock with matching ticker is updated or removed
    # RAISES:
    #   -ServiceError; database call fails
    def execute_sell(self, user_account : User, portfolio : Portfolio, shares_requested : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: add funds to user account
        
        ticker, quantity = shares_requested

        try:

            if portfolio.has_stock(ticker) and quantity == portfolio.stocks[ticker].quantity:
                # TODO: remove from the db
                pass
            else:
                # TODO: update the db
                pass

        except DatabaseError as e:
            raise ServiceError("Failed to execute sell") from e

        portfolio.sell_shares(shares_requested)


    # INPUT:
    #   -credentials(tuple[str,str]); user login and password
    # OUTPUT:
    #   -match(bool); do credentials match
    # PRECONDITION:
    #   -credentials; login and password are non empty
    # POSTCONDITION:
    #   -match; True if credentials exist in db, False otherwise
    # RAISES:
    #   -ServiceError; database call fails
    def credentials_match(self, credentials : tuple[str, str]) -> bool:
        try:

            u_id = self.db.resolve_credentials(credentials)

        except DatabaseError as e:
            raise ServiceError("Failed to match credentials") from e

        match = u_id != None

        return match 


    # INPUT:
    #   -portfolio(Portfolio); a user portfolio
    # OUTPUT:
    #   -packaged_data(list[dict[str,str|int]]); explicit labeler for each stock pair "ticker", "quantity" labels  
    # PRECONDITION: None
    # POSTCONDITION:
    #   -packaged_data; represents a labeled set of all stocks in portfolio
    # RAISES: None
    def package_portfolio_data(self, portfolio : Portfolio) -> list[dict[str, str | int]]:
        packaged_data = []

        for stock in portfolio.stocks.values():
            packaged_data.append({"ticker": stock.ticker, "quantity": stock.quantity})

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
    #RAISES: None
    def retrieve_stored_data(self, login : str) -> tuple[tuple, list[tuple], list[tuple]]:
        stored_user = self.db.pull_user(login)
        stored_portfolios = self.db.pull_portfolios(stored_user[0])
        stored_stocks = self.db.pull_stocks(stored_user[0])

        return stored_user, stored_portfolios, stored_stocks


    # INPUT:
    #   -stored_stocks(list[tuple]); all user stocks listed as portfolio id, stock id, ticker, quantity
    # OUTPUT:
    #   -portfolio_assignments(dict[int, list[tuple]]); list of stock data keyed to specific portfolio id
    # PRECONDITION:
    #   -stored_stocks; see Database.pull_stocks() POSTCONDITION
    # POSTCONDITION:
    #   -portfolio_assignments; every portfolio id is uniquely keyed to its stock list
    # RAISES: None
    def assign_portfolio_allocations(self, stored_stocks : list[tuple]) -> dict[int, list[tuple]]:
        portfolio_assignments = defaultdict(list)
        for stock in stored_stocks:
            p_id = stock[0]
            portfolio_assignments[p_id].append(stock[1:])

        return portfolio_assignments


    # INPUT:
    #   -user_account(User); current user account
    #   -login(str); user login
    # OUTPUT: None
    # PRECONDITION:
    #   -login; a user with this login exists in the database
    # POSTCONDITION:
    #   -user_account; is populated with id, login, balance, all portfolios and respective stocks from database
    # RAISES: None
    def populate_user_account(self, user_account : User, login : str) -> None:
        stored_user, stored_portfolios, stored_stocks = self.retrieve_stored_data(login)

        user_account.id, user_account.login, user_account.balance = stored_user

        self.populate_user_portfolios(user_account.portfolios, stored_portfolios, stored_stocks)
        

    # INPUT: keyed dict of all user portfolios, list of all stored portfolio tuples, list of all stored stock tuples
    # OUTPUT: None
    # PRECONDITION: in memory user portfolios are empty, stored portfolios contains all database data related to user portfolios as does stored stocks
    # POSTCONDITION: in memory user account portfolios are all populated
    def populate_user_portfolios(self, user_portfolios : dict[str, Portfolio], stored_portfolios : list[tuple], stored_stocks : list[tuple]) -> None:
        stored_stocks = self.assign_portfolio_allocations(stored_stocks)

        for portfolio in stored_portfolios:

            p_id = portfolio[0]
            p_name = portfolio[1]

            user_portfolios[p_name] = Portfolio(id=p_id,name=p_name)

            self.populate_portfolio_stocks(user_portfolios[p_name].stocks, stored_stocks.get(p_id, []))
    

    # INPUT: a dict of all in memory portfolio stocks, a list of tuples of all stored stocks related to portfolio 
    # OUTPUT: None
    # PRECONDITION: stored portfolio stocks contain all stocks related to the current portfolio
    # POSTCONDITION: user portfolio is populated with its respective stocks
    def populate_portfolio_stocks(self, portfolio_stocks : dict[str, Stock], stored_portfolio_stocks : list[tuple]) -> None:

        for stock in stored_portfolio_stocks:

            s_id = stock[0]
            s_ticker = stock[1]
            s_quantity = stock[2]

            portfolio_stocks[s_ticker] = Stock(id=s_id, ticker=s_ticker, quantity=s_quantity)


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION: Application is running
    # POSTCONDITION: Application is terminated
    @staticmethod
    def exit_app() -> None:
        sys.exit(0)