from common.errors import ServiceError


# PURPOSE: 
#   -Cli provides a user interaction abstraction
#   -Handles all user interaction and enforces program control flow
class Cli:
    def __init__(self, service, sanitizer, validator, visualizer):
        self.user_account = None
        self.serv = service
        self.validator = validator
        self.vis = visualizer
        self.san = sanitizer


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -self.user_account; is None
    # POSTCONDITION:
    #   -terminal; initial startup menu is displayed
    # RAISES: None
    def execute(self) -> None:
        self.display_startup_menu()


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -Cli; navigates to credential gatherer (new/login), user dashboard (login success), or exits
    # RAISES: None
    def display_startup_menu(self) -> None:
        while True:
            self.user_account = None

            print("==============================")
            print("Welcome to our Investment App!")
            print("==============================\n")

            print("1. Create an account")
            print("2. Login")
            print("3. Exit application")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if selection == 1:
                self.display_account_credential_gatherer(new=True)
            elif selection == 2:
                self.display_account_credential_gatherer(new=False)
            elif selection == 3:
                self.serv.exit_app()
            else:
                print('Invalid selection!')

            if self.user_account is not None:
                self.display_user_dashboard(self.user_account)


    # INPUT: 
    #   -new(bool); True if creating a new account, False if logging in
    # OUTPUT: None
    # PRECONDITION:
    #   -new; True or False
    # POSTCONDITION:
    #   -self.user_account; if confirmed, see Service.create_account() or Service.find_account() POSTCONDITION, otherwise unchanged
    #   -Cli; returns to caller on confirm or cancel
    # RAISES: None  
    def display_account_credential_gatherer(self, new : bool) -> None:
        print(f"---------------{'SIGNUP' if new else 'LOGIN'}---------------")
        login = input('Enter your login: ')
        password = input('Enter your password: ')
        print(f"---------------{'------' if new else '-----'}---------------")

        creds = login, password
        creds = self.san.sanitize_credentials(creds)

        result = self.validator.account_validator(creds, new)
            

        while True:
            print("1. Confirm")
            print("2. Cancel")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if selection == 1:

                if not result.valid:
                    print(result.reason)
                    return

                try:

                    if new:
                        self.user_account = self.serv.create_account(creds)
                    else:
                        self.user_account = self.serv.find_account(login)

                    print(result.reason)    

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue
                    
            elif selection != 2:
                print("Invalid selection!")
                continue

            return


    # INPUT:
    #   -user_account(User); current user account
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; fully populated and up to date
    # POSTCONDITION:
    #   -Cli; navigates to portfolio contents, funding menu, portfolio modification menu, returns on logout, or exits
    # RAISES: None 
    def display_user_dashboard(self, user_account) -> None:
        while True:
            num_portfolios = len(user_account.portfolios)
            portfolio_list = list(user_account.portfolios.values())
            print("-------------------DASHBOARD---------------------")
            print(f"Hello, {user_account.login}")
            print(f"Current Balance: ${user_account.balance:,.2f}\n")

            for i in range(num_portfolios):
                print(f"{i + 1}. {portfolio_list[i].name}")

            print(f"{num_portfolios + 1}. Add Funds")
            print(f"{num_portfolios + 2}. Create Portfolio")
            print(f"{num_portfolios + 3}. Remove Portfolio")
            print(f"{num_portfolios + 4}. Logout")
            print(f"{num_portfolios + 5}. Exit application")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if 0 < selection <= num_portfolios:
                r = self.display_portfolio_contents(portfolio_list[selection - 1])
                if r == "logout":
                    return
            elif selection == num_portfolios + 1:
                self.display_funding_menu(user_account)
            elif selection == num_portfolios + 2:
                self.display_portfolio_modification_menu(user_account, create = True)
            elif selection == num_portfolios + 3:
                self.display_portfolio_modification_menu(user_account, create = False)
            elif selection == num_portfolios + 4:
                return
            elif selection == num_portfolios + 5:
                self.serv.exit_app()
            else:
                print('Invalid selection!')
                
    
    # INPUT: 
    #   -user_account(User); current user account
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; fully populated and up to date
    # POSTCONDITION:
    #   -user_account; if confirmed see Service.fund_account() POSTCONDITION, otherwise unchanged
    #   -Cli; returns to user dashboard
    # RAISES: None
    def display_funding_menu(self, user_account) -> None:
        print("------------ Fund Account ------------")

        funds_request = input("Enter amount: "); print()

        funds_request = self.san.sanitize_funds_request(funds_request)
    
        result = self.validator.fund_validator(funds_request)

        while True:
            print("1. Confirm")
            print("2. Cancel")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if selection == 1:

                if not result.valid:
                    print(result.reason)
                    return

                try:

                    self.serv.fund_account(user_account, funds_request)
                    print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue
            elif selection != 2:
                print("Invalid selection!")
                continue

            return


    # INPUT:
    #   -user_account(User); current user account
    #   -create(bool); True if creating a new portfolio, False if removing one
    # OUTPUT: None
    # PRECONDITION:
    #   -user_account; fully populated and up to date
    #   -create; True or False
    # POSTCONDITION:
    #   -user_account; if confirmed see Service.create_portfolio() or Service.remove_portfolio() POSTCONDITION, otherwise unchanged
    #   -Cli; returns to user dashboard
    # RAISES: None
    def display_portfolio_modification_menu(self, user_account, create : bool) -> None:
        print("-------------- Portfolio Modification Menu ------------------")

        name_request = input("Enter portfolio name: ").strip()
        name_request = self.san.sanitize_portfolio_name(name_request)

        result = self.validator.portfolio_validator(user_account, name_request, create)

        while True:
            print("1. Confirm")
            print("2. Cancel")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if selection == 1:

                if not result.valid:
                    print(result.reason)
                    return

                try:

                    if create:
                        self.serv.create_portfolio(user_account, name_request)
                    else:
                        self.serv.remove_portfolio(user_account, name_request)

                    print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue

            elif selection != 2:
                # TODO: invalid selection error msg
                print("Invalid selection!")
                continue

            return


    # INPUT: 
    #   -portfolio(Portfolio); a user portfolio
    # OUTPUT:
    #   -return(str | None); "logout" if user selects logout, None otherwise
    # PRECONDITION:
    #   -portfolio; fully populated and up to date
    # POSTCONDITION:
    #   -Cli; navigates to stock transaction menu (buy/sell), returns on back, returns "logout" on logout, or exits
    # RAISES: None
    def display_portfolio_contents(self, portfolio) -> str | None:
        while True:
            num_stocks = len(portfolio.stocks)
            stock_list = list(portfolio.stocks.values())
            print(f"-------------------{portfolio.name}-----------------------")
            for i in range(num_stocks):
                print(f"|{stock_list[i].ticker} {stock_list[i].quantity}|")

            print("1. Buy Stock")
            print("2. Sell Stock")
            print("3. Go Back")
            print("4. Logout")
            print("5. Exit application")

            self.vis.display_pie_chart(lambda: self.serv.package_portfolio_data(portfolio))
            selection = input("Select option: "); print()
            selection = self.san.sanitize_selection(selection)

            self.vis.close_chart()

            if selection == 1:
                self.display_stock_transaction_menu(portfolio, purchase=True)
            elif selection == 2:
                self.display_stock_transaction_menu(portfolio, purchase=False)
            elif selection == 3:
                return
            elif selection == 4:
                return "logout"
            elif selection == 5:
                self.serv.exit_app()
            else:
                print("Invalid Selection!")
           

    # INPUT:
    #   -portfolio(Portfolio); a user portfolio
    #   -purchase(bool); True if purchasing a stock, False if selling
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio; fully populated and up to date
    #   -purchase; True or False
    #   -self.user_account; fully populated and up to date
    # POSTCONDITION:
    #   -portfolio; if confirmed see Service.execute_buy() or Service.execute_sell() POSTCONDITION, otherwise unchanged
    #   -Cli; returns to portfolio menu
    # RAISES: None 
    def display_stock_transaction_menu(self, portfolio, purchase : bool) -> None:
        print("------------- Stock Transaction ---------------")
           
        ticker = input("Enter stock ticker (e.g., AAPL): ")
        quantity = input(f"Enter number of shares to {'buy' if purchase else 'sell'}: "); print()
            
        shares_request = ticker, quantity
        shares_request = self.san.sanitize_shares_request(shares_request)

        result = self.validator.shares_request_validator(portfolio, shares_request, self.user_account.balance, purchase)
            
        while True:
            print("1. Submit")
            print("2. Cancel")
            selection = input("Select option: "); print()

            selection = self.san.sanitize_selection(selection)

            if selection == 1:

                if not result.valid:
                    print(result.reason)
                    return

                try:

                    if purchase:
                        self.serv.execute_buy(self.user_account, portfolio, shares_request)
                    else:
                        self.serv.execute_sell(self.user_account, portfolio, shares_request)

                    print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue

            elif selection != 2:
                print("Invalid selection!")
                continue

            return