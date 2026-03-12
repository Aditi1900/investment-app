from service import Service as serv
from visualizer import Visualizer as vis
from validator import Validator as validator


class Cli:

    def __init__(self):
        self.userAccount = None


    def display_startup_menu(self):

        while True:
            selection = 0
            self.userAccount = None
            # TODO: Welcome menu display
            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                self.display_account_credential_gatherer(isNew=True)
                continue
            elif selection == 2:
                self.display_account_credential_gatherer(isNew=False)
            elif selection == 3:
                serv.exitApp()
            else:
                # TODO: invalid selection error msg
                continue

            self.display_user_dashboard(self.userAccount)


    def display_account_credential_gatherer(self, isNew):  

        isValid = False

        while True:
            # TODO: Login/Signup menu display
            # TODO: Credential input receiver (login & password) 

            creds = login, password

            isValid = validator.account_validator(creds, isNew)

            if isValid:
                break

            # TODO: invalid credentials error msg


        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                if isNew:
                    self.userAccount = serv.create_account(creds)
                    # TODO: Msg that indicates a action was successfully performed
                else:
                    self.userAccount = serv.find_account(creds)

            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return


    def display_user_dashboard(self, userAccount):

        while True:
            selection = 0
            numPortfolios = len(userAccount.portfolios)

            # TODO: User dashboard display
            # TODO: Display selection options
            # TODO: Selection input receiver

            if 0 < selection <= numPortfolios:
                r = self.display_portfolio_contents(userAccount.portfolios[selection - 1])
                if r == "back":
                    return
            elif selection == numPortfolios + 1:
                self.display_portfolio_creation_menu(userAccount)
            elif selection == numPortfolios + 2:
                return
            elif selection == numPortfolios + 3:
                serv.exitApp()
            else:
                # TODO: invalid selection error msg
                pass  # Remove this once you implement


    def display_portfolio_creation_menu(self, userAccount):

        isValid = False

        while True:
            # TODO: Portfolio creation display
            # TODO: Portfolio name input receiver

            name = name

            isValid = validator.portfolio_validator(name)

            if isValid:
                break

            # TODO: invalid name error msg


        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                portfolio = serv.create_portfolio(userAccount, name)
                # TODO: Msg that indicates a action was successfully performed
            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return


    def display_portfolio_contents(self, portfolio):

        while True:
            selection = 0

            # TODO: Portfolio contents display
            # TODO: Display selection options
            # TODO: Selection input receiver

            vis.display_pie_chart(portfolio)

            if selection == 1:
                self.display_stock_transaction_menu(portfolio=portfolio, isPurchase=True)
            elif selection == 2:
                self.display_stock_transaction_menu(portfolio=portfolio, isPurchase=False)
            elif selection == 3:
                return
            elif selection == 4:
                return "back"
            elif selection == 5:
                serv.exitApp()
            else:
                # TODO: invalid selection error msg
                pass  # Remove this once you implement


    def display_stock_transaction_menu(self, portfolio, isPurchase):

        while True:
            # TODO: Transaction menu display
            # TODO: Stocks input receiver (ticker & quantity) 

            stocks = ticker, quantity

            isValidTicker = validator.stock_ticker_validator(ticker, isPurchase, portfolio)
            if isValidTicker != True:
                # TODO: invalid ticker error msg
                continue

            isValidQuantity = validator.stock_quantity_validator(stocks, isPurchase, portfolio)
            if isValidQuantity != True:
                # TODO: invalid quantity error msg
                continue

            isValidBalance = validator.sufficient_balance_validator(stocks, isPurchase, self.userAccount.balance)
            if isValidBalance != True:
                # TODO: invalid selection error msg
                continue

            break


        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                if isPurchase:
                    serv.execute_buy(portfolio, stocks)
                    # TODO: Msg that indicates a action was successfully performed
                else:
                    serv.execute_sell(portfolio, stocks)
                    # TODO: Msg that indicates a action was successfully performed

            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return