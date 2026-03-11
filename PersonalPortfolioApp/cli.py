from service import Service as serv
from visualizer import Visualizer as vis
from validator import Validator as validator


class Cli:

    def __init__(self):
        self.userAccount = None



    def display_startup_menu(self):
        #welcome menu display goes here
        while(True):
            selection = 0
            #Selection input reciever goes here

            if(selection == 1):
                self.display_account_credential_gatherer(isNew = True)
            elif(selection == 2):
                self.display_account_credential_gatherer(isNew = False)
            elif(selection == 3):
                serv.exitApp()
            else:
                #invalid input error goes here
                print()
                continue

            self.display_user_dashboard(self.userAccount)



    def display_account_credential_gatherer(self, isNew):  
        selection = 0

        isValid = False

        while(isValid != True):
            #User Input Reciever Logic goes here
        
            creds = login, password
        
       
            isValid = validator.account_validator(creds, isNew)
            
            if(isValid != True):
                #Invalid creds message goes here
                print()

        
        while(True):
            #add user selection logic here

            if(selection == 1):
                if(isNew):
                    self.userAccount = serv.create_account(creds)
                else:
                    self.userAccount = serv.find_account(creds)

            elif(selection != 2):
                #invalid input message goes here
                print()
                continue

            return


    def display_user_dashboard(self, userAccount):
        
        while(True):
            selection = 0
            numPortfolios = len(userAccount.portfolios)

            #Any remaining display logic for user dashboard here

            if(selection > 0 and selection <= numPortfolios):
                r = self.display_portfolio_contents(userAccount.portfolios[selection - 1])
                if (r == "back"): return
            elif(selection == numPortfolios + 1):
                self.display_portfolio_creation_menu(userAccount)
            elif(selection == numPortfolios + 2):
                return
            elif(selection == numPortfolios + 3):
                serv.exitApp()
            else:
                #invalid input message goes here
                print()



    def display_portfolio_creation_menu(self, userAccount):
        selection = 0
        #portfolio creation display here
        
        isValid = False

        while(isValid != True):
            #User Input Reciever Logic goes here

            name = name
        
            isValid = validator.portfolio_validator(name)
            
            if(isValid != True):
                #Invalid name message goes here
                print()
        
        while(True):
            #add user selection logic here

            if(selection == 1):
                portfolio = serv.create_portfolio(userAccount, name)
            elif(selection != 2):
                #invalid input message goes here
                print()
                continue

            return
        


    def display_portfolio_contents(self, portfolio):
        while(True):
            selection = 0
            #portfolio display code goes here
            vis.display_pie_chart(portfolio.getAllocation())

            if(selection == 1):
                self.display_stock_transaction_menu(portfolio = portfolio, isPurchase = True)
            elif(selection == 2):
                self.display_stock_transaction_menu(portfolio = portfolio, isPurchase = False)
            elif(selection == 3):
                return
            elif(selection == 4):
                return "back"
            elif(selection == 5):
                serv.exitApp()

    def display_stock_transaction_menu(self, portfolio, isPurchase):
        
        selection = 0

        while(True):

            #User Input Reciever Logic goes here
            
            stocks = ticker, quantity
        
            
            isValidTicker = validator.stock_ticker_validation(ticker, isPurchase, portfolio)
            if(isValidTicker != True):
                #Invalid stock message goes here
                print()
                continue

            isValidQuantity = validator.stock_quantity_validation(stocks, isPurchase, portfolio)
            if(isValidQuantity != True):
                #Invalid stock message goes here
                print()
                continue

            isValidBalance = validator.stock_price(stocks, isPurchase, self.userAccount.balance)
            if(isValidBalance != True):
                #Invalid stock message goes here
                print()
                continue
        

            break
            

        
        while(True):
            #add user selection logic here

            if(selection == 1):
                if(isPurchase):
                    serv.execute_buy(portfolio, stocks)
                else:
                    serv.execute_sell(portfolio, stocks)

            elif(selection != 2):
                #invalid input message goes here
                print()
                continue

            return




