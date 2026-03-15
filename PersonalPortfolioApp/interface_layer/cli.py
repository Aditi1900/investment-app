# PURPOSE:
class Cli:

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def __init__(self, service, validator, visualizer):
        self.userAccount = None
        self.serv = service
        self.validator = validator
        self.vis = visualizer


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def execute(self):
        self.display_startup_menu()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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
                self.serv.exitApp()
            else:
                # TODO: invalid selection error msg
                continue

            self.display_user_dashboard(self.userAccount)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_account_credential_gatherer(self, isNew):

        isValid = False

        while True:
            # TODO: Login/Signup menu display
            # TODO: Credential input receiver (login & password)

            creds = login, password

            isValid = self.validator.account_validator(creds, isNew)

            if isValid:
                break

            # TODO: invalid credentials error msg


        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                if isNew:
                    self.userAccount = self.serv.create_account(creds)
                    # TODO: Msg that indicates a action was successfully performed
                else:
                    self.userAccount = self.serv.find_account(login)

            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_user_dashboard(self, userAccount):

        while True:
            selection = 0
            numPortfolios = len(userAccount.portfolios)

            # TODO: User dashboard display
            # TODO: Display selection options
            # TODO: Selection input receiver

            portfolio_list = list(userAccount.portfolios.values())

            if 0 < selection <= numPortfolios:
                r = self.display_portfolio_contents(portfolio_list[selection - 1])
                if r == "back":
                    return
            elif selection == numPortfolios + 1:
                self.display_funding_menu(userAccount)
            elif selection == numPortfolios + 2:
                self.display_portfolio_modification_menu(userAccount, create = True)
            elif selection == numPortfolios + 3:
                self.display_portfolio_modification_menu(userAccount, create = False)
            elif selection == numPortfolios + 4:
                return
            elif selection == numPortfolios + 5:
                self.serv.exitApp()
            else:
                # TODO: invalid selection error msg
                pass  # Remove this once you implement

    
    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_funding_menu(self, userAccount):

        isValid = False

        while True :
            # TODO: Account Funding display
            # TODO: Funds input reciever

            funds_to_add = funds_to_add

            isValid = self.validator.fund_validator(funds_to_add)

            if isValid:
                break

            # TODO: invalid funds error msg

        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                self.serv.fund_account(userAccount = userAccount, funds = funds_to_add)
                # TODO: Msg that indicates a action was successfully performed
            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_portfolio_modification_menu(self, userAccount, create):

        isValid = False

        while True:
            # TODO: Portfolio creation display
            # TODO: Portfolio name input receiver

            name = name

            isValid = self.validator.portfolio_validator(userAccount, name, create)

            if isValid:
                break

            # TODO: invalid name error msg


        while True:
            selection = 0

            # TODO: Display selection options
            # TODO: Selection input receiver

            if selection == 1:
                if(create):
                    self.serv.create_portfolio(userAccount=userAccount, portfolioName=name)
                    # TODO: Msg that indicates a action was successfully performed
                else:
                    self.serv.remove_portfolio(userAccount=userAccount, portfolioName=name)
                    # TODO: Msg that indicates a action was successfully performed
            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_portfolio_contents(self, portfolio):

        

        while True:
            selection = 0

            # TODO: Portfolio contents display
            # TODO: Display selection options
            # TODO: Selection input receiver
            
            data = [{"ticker": s.ticker, "quantity": s.quantity} for s in portfolio.stocks.values()]
            self.vis.display_pie_chart(data)

            if selection == 1:
                self.display_stock_transaction_menu(portfolio=portfolio, isPurchase=True)
            elif selection == 2:
                self.display_stock_transaction_menu(portfolio=portfolio, isPurchase=False)
            elif selection == 3:
                return
            elif selection == 4:
                return "back"
            elif selection == 5:
                self.serv.exitApp()
            else:
                # TODO: invalid selection error msg
                pass  # Remove this once you implement


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_stock_transaction_menu(self, portfolio, isPurchase):

        while True:
            # TODO: Transaction menu display
            # TODO: shares_requested input receiver (ticker & quantity)

            shares_requested = ticker, quantity

            isValidTicker = self.validator.stock_ticker_validator(portfolio, ticker, isPurchase)
            if isValidTicker != True:
                # TODO: invalid ticker error msg
                continue

            isValidQuantity = self.validator.stock_quantity_validator(portfolio, shares_requested, isPurchase)
            if isValidQuantity != True:
                # TODO: invalid quantity error msg
                continue

            isValidBalance = self.validator.sufficient_balance_validator(
                self.userAccount.balance,
                shares_requested,
                isPurchase
            )
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
                    self.serv.execute_buy(
                        userAccount=self.userAccount,
                        portfolio=portfolio,
                        stock_dat=shares_requested
                    )
                    # TODO: Msg that indicates a action was successfully performed
                else:
                    self.serv.execute_sell(
                        userAccount=self.userAccount,
                        portfolio=portfolio,
                        stock_dat=shares_requested
                    )
                    # TODO: Msg that indicates a action was successfully performed

            elif selection != 2:
                # TODO: invalid selection error msg
                continue

            return