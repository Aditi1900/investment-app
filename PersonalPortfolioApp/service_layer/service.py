import sys
from collections import defaultdict
from domain_models import *


# PURPOSE:
class Service:
    def __init__(self, database):
        self.db = database


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def create_account(self, credentials : tuple[str, str]) -> None:
        # TODO: Add user to the db
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def find_account(self, login : str) -> User:
        # TODO: Create user object
        # TODO: Populate user object
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def fund_account(self, user_account : User, funds_request : float) -> None:
        #TODO: update db funds
        user_account.add_funds(funds_request)
        


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def create_portfolio(self, user_account : User, portfolio_name : str) -> None:
        p_id = self.db.insert_portfolio(user_account.id, portfolio_name)
        # TODO: add new empty portfolio to user_account object
        user_account.portfolios[portfolio_name].id = p_id


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def remove_portfolio(self, user_account : User, portfolio_name : str) -> None:
        #TODO: call remove function for removing portfolio from db
        user_account.remove_portfolio(portfolio_name)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def execute_buy(self, user_account : User, portfolio : Portfolio, shares_requested : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: subtract funds from user account
        
        ticker, quantity = shares_requested

        s_id = None

        if portfolio.has_stock(ticker):
            # TODO: update the db
            pass
        else:
             s_id = self.db.insert_stock(portfolio.id, shares_requested)
             
        portfolio.buy_shares(shares_requested)

        if s_id != None:
            portfolio.stocks[ticker].id = s_id
        

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def execute_sell(self, user_account : User, portfolio : Portfolio, shares_requested : tuple[str, int]) -> None:
        # TODO: call api to get stock price
        # TODO: add funds to user account
        # TODO: remove the stock(s) from the portfolio
        
        ticker, quantity = shares_requested

        if portfolio.has_stock(ticker) and quantity == portfolio.stocks[ticker].quantity:
            # TODO: remove from the db
            pass
        else:
            # TODO: update the db
            pass

        portfolio.sell_shares(shares_requested)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def user_exists_in_storage(self, login : str) -> bool:
        u_id = self.db.resolve_user_id(login)
        return u_id != None


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def retrieve_stored_data(self, login : str) -> tuple[tuple, list[tuple], list[tuple]]:
       
        stored_user = self.db.pull_user(login)
        stored_portfolios = self.db.pull_portfolios(stored_user[0])
        stored_stocks = self.db.pull_stocks(stored_user[0])

        
        

        return stored_user, stored_portfolios, stored_stocks


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def assign_portfolio_allocations(self, stored_stocks : list[tuple]) -> dict[int, list[tuple]]:
        portfolio_assignments = defaultdict(list)
        for stock in stored_stocks:
            p_id = stock[0]
            portfolio_assignments[p_id].append(stock[1:])

        return portfolio_assignments


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_user_account(self, user_account : User, login : str) -> None:
        stored_user, stored_portfolios, stored_stocks = self.retrieve_stored_data(login)

        user_account.id, user_account.login, user_account.password, user_account.balance = stored_user

        self.populate_user_portfolios(user_account.portfolios, stored_portfolios, stored_stocks)
        

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_user_portfolios(self, user_portfolios : dict[str, Portfolio], stored_portfolios : list[tuple], stored_stocks : list[tuple]) -> None:
        stored_stocks = self.assign_portfolio_allocations(stored_stocks)

        for portfolio in stored_portfolios:

            p_id = portfolio[0]
            p_name = portfolio[1]

            user_portfolios[p_name] = Portfolio(id=p_id,name=p_name)

            self.populate_portfolio_stocks(user_portfolios[p_name].stocks, stored_stocks.get(p_id, []))
    

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_portfolio_stocks(self, portfolio_stocks : dict[str, Stock], stored_portfolio_stocks : list[tuple]) -> None:

        for stock in stored_portfolio_stocks:

            s_id = stock[0]
            s_ticker = stock[1]
            s_quantity = stock[2]

            portfolio_stocks[s_ticker] = Stock(id=s_id, ticker=s_ticker, quantity=s_quantity)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def exit_app() -> None:
        sys.exit(0)