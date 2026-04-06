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

            # TODO: Welcome menu display
            print("Welcome to our investment portfolio app!\nWhat would you like to do?\n")
           
            # TODO: Display selection options
            print("1. Create an account\n")
            print("2. Login\n")
            print("3. Exit application\n")

            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if selection == 1:
                self.display_account_credential_gatherer(new=True)
                continue
            elif selection == 2:
                self.display_account_credential_gatherer(new=False)
            elif selection == 3:
                self.serv.exit_app()
            else:
                # TODO: invalid selection error msg
                print('Invalid selection.\n')
                continue

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
        result = None
        while True:
            print('---------------LOGIN/SIGNUP---------------\n')
            
            login = input('Enter your login:')
            password = input('Enter your password:')

            creds = login, password
            creds = self.san.sanitize_credentials(creds)

            result = self.validator.account_validator(creds, new)

            if result.valid:
                break

            # TODO: invalid credentials error msg
            print(result.reason)


        while True:
            # TODO: Display selection options
            print("\n1. Confirm")
            print("2. Cancel")

            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if selection == 1:
                try:

                    if new:
                        self.user_account = self.serv.create_account(creds)
                        # TODO: Msg that indicates a action was successfully performed
                        print(result.reason)
                    else:
                        self.user_account = self.serv.find_account(login)
                        #additional
                        print(result.reason)
                        
                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue
                    
            elif selection != 2:
                # TODO: invalid selection error msg
                print("Invalid selection.\n")
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
            numPortfolios = len(user_account.portfolios)
            portfolio_list = list(user_account.portfolios.values())

            # TODO: User dashboard display
            print("-------------------DASHBOARD---------------------\n")
            
            # Greets the user and displays the balance
            print("Hello,", user_account.username)
            print("Current Balance: $", user_account.balance, "\n")

            # Portfolio list
            for i in range(numPortfolios):
                print(i + 1, ".", portfolio_list[i].name)
                
            # TODO: Display selection options
            print(numPortfolios + 1, ". Add Funds")
            print(numPortfolios + 2, ". Create Portfolio")
            print(numPortfolios + 3, ". Remove Portfolio")
            print(numPortfolios + 4, ". Logout")
            print(numPortfolios + 5, ". Exit")
            
            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if 0 < selection <= numPortfolios:
                r = self.display_portfolio_contents(portfolio_list[selection - 1])
                if r == "logout":
                    return
            elif selection == numPortfolios + 1:
                self.display_funding_menu(user_account)
            elif selection == numPortfolios + 2:
                self.display_portfolio_modification_menu(user_account, create = True)
            elif selection == numPortfolios + 3:
                self.display_portfolio_modification_menu(user_account, create = False)
            elif selection == numPortfolios + 4:
                return
            elif selection == numPortfolios + 5:
                self.serv.exit_app()
            else:
                # TODO: invalid selection error msg
                print('Invalid selection!\n')
                
    
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
        result = None
        while True :
            # TODO: Account Funding display
            print("\n------------ Fund Account ------------")
            
            # TODO: Funds input reciever
            funds_request = input("Enter amount: ")
            funds_request = self.san.sanitize_funds_request(funds_request)

            result = self.validator.fund_validator(funds_request)

            if result.valid:
                break

            # TODO: invalid funds error msg
            print(result.reason)

        while True:
            # TODO: Display selection options
            print("\n1. Confirm")
            print("2. Cancel")

            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if selection == 1:
                try:

                    self.serv.fund_account(user_account, funds_request)
                    # TODO: Msg that indicates a action was successfully performed
                    print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue
            elif selection != 2:
                # TODO: invalid selection error msg
                print("Invalid selection/n")
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
        result = None
        while True:
            # TODO: Portfolio creation display
            print("\n-------------- Portfolio Modification Menu ------------------")

            # TODO: Portfolio name input receiver

            name_request = input("Enter portfolio name: ").strip()
            name_request = self.san.sanitize_portfolio_name(name_request)

            result = self.validator.portfolio_validator(user_account, name_request, create)

            if result.valid:
                break

            # TODO: invalid name error msg
            print(result.reason)


        while True:
            # TODO: Display selection options
            print("1. Submit\n")
            print("2. Cancel\n")

            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if selection == 1:
                try:

                    if create:
                        self.serv.create_portfolio(user_account, name_request)
                        # TODO: Msg that indicates a action was successfully performed
                        print(result.reason)
                        
                    else:
                        self.serv.remove_portfolio(user_account, name_request)
                        # TODO: Msg that indicates a action was successfully performed
                        print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue
            elif selection != 2:
                # TODO: invalid selection error msg
                print("Invalid selection/n")
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
            packaged_data = self.serv.package_portfolio_data(portfolio)
            
            self.vis.display_pie_chart(packaged_data)

            # TODO: Portfolio contents display
            print("-------------------USER PORTFOLIO-----------------------")
            
            # TODO: Display selection options
            print("Select an option:\n")
            print("1. Buy Stock\n")
            print("2. Sell Stock\n")
            print("3. Go Back\n")
            print("4. Logout\n")
            print("5. Exit\n")

            # TODO: Selection input receiver
            selection = input("Select option: ")
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
                # TODO: invalid selection error msg
                print("Invalid Selection/n")
           

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
        result = None
        while True:
            # TODO: Transaction menu display
            print("\n------------- Stock Transaction ---------------")
            
            # TODO: shares_request input receiver (ticker & quantity)
            ticker = input("Enter stock ticker (e.g., AAPL): ")
            quantity = input("Enter number of shares to buy/sell: ")
            
            shares_request = ticker, quantity
            shares_request = self.san.sanitize_shares_request(shares_request)

            result = self.validator.shares_request_validator(portfolio, shares_request, self.user_account.balance, purchase)
            
            if result.valid:
                break;

            print(result.reason)


        while True:
            # TODO: Display selection options
            print("What would you like to do?\n")
            print("1. Submit\n")
            print("2. Cancel\n")

            # TODO: Selection input receiver
            selection = input("Select option: ")
            selection = self.san.sanitize_selection(selection)

            if selection == 1:

                try:

                    if purchase:
                        self.serv.execute_buy(self.user_account, portfolio, shares_request)
                        # TODO: Msg that indicates a action was successfully performed
                        print(result.reason)
                    else:
                        self.serv.execute_sell(self.user_account, portfolio, shares_request)
                        # TODO: Msg that indicates a action was successfully performed
                        print(result.reason)

                except ServiceError as e:
                    print(f"ERROR: {e}")
                    continue

            elif selection != 2:
                # TODO: invalid selection error msg
                print("Invalid selection/n")
                continue

            return