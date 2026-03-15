import sys
from domain_models import *


# PURPOSE:
class Service:

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def __init__(self, database):
        self.db = database


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def create_account(self, credentials) -> User:
        # TODO: Add user to the db
        # TODO: Create user and return object
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def find_account(self, login) -> User:
        # TODO: Create, Populate and return user object
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def fund_account(self, userAccount, funds):
        userAccount.add_funds(funds)
        #TODO: update db funds
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def create_portfolio(self, userAccount, portfolioName) -> None:
        # TODO: add new empty portfolio to userAccount object
        userAccount.portfolios[portfolioName].id = self.db.insert_portfolio(
            user_id=userAccount.id,
            portfolioName=portfolioName
        )
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def remove_portfolio(self, userAccount, portfolioName) -> None:
        userAccount.remove_portfolio(portfolioName)
        #TODO: call remove function for removing portfolio from db
        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def execute_buy(self, userAccount, portfolio, stock_dat) -> None:
        # TODO: call api to get stock price
        # TODO: subtract funds from user account
        # TODO: add the stock(s) to the portfolio
        r = portfolio.buy_shares(stock_dat)
        s_id = r[0]
        flag = r[1]

        if flag == "new":
            portfolio.stocks[stock_dat[0]].id = self.db.insert_stock(
                portfolio_id=portfolio.id,
                stock_dat=stock_dat
            )
        else:
            # TODO: update the db
            pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def execute_sell(self, userAccount, portfolio, stock_dat) -> None:
        # TODO: call api to get stock price
        # TODO: add funds to user account
        # TODO: remove the stock(s) from the portfolio
        r = portfolio.sell_shares(stock_dat)
        s_id = r[0]
        flag = r[1]

        if flag == "removed":
            # TODO: remove from the db
            pass
        else:
            # TODO: update the db
            pass

        pass


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def user_exists_in_storage(self, login) -> bool:
        u_id = self.db.resolve_user_id(login)
        return u_id != None


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_user(self, userAccount, login):
        user_info = self.db.pull_user(login)

        userAccount.id = user_info[0]
        userAccount.login = user_info[1]
        userAccount.password = user_info[2]
        userAccount.balance = user_info[3]

        self.populate_user_portfolios(
            user_id=userAccount.id,
            portfolios=userAccount.portfolios
        )


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_user_portfolios(self, user_id, portfolios):
        stored_portfolios = self.db.pull_portfolios(user_id)

        for portfolio in stored_portfolios:
            portfolios[portfolio[1]] = Portfolio(
                id=portfolio[0],
                name=portfolio[1]
            )

            self.populate_portfolio_stocks(
                portfolio_id=portfolio[0],
                stocks=portfolios[portfolio[1]].stocks
            )


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def populate_portfolio_stocks(self, portfolio_id, stocks):
        stored_stocks = self.db.pull_stocks(portfolio_id)

        for stock in stored_stocks:
            stocks[stock[1]] = Stock(
                id=stock[0],
                ticker=stock[1],
                quantity=stock[2]
            )


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    @staticmethod
    def exitApp():
        sys.exit(0)