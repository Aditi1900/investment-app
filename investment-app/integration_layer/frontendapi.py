from common.errors import ValidationError

class FrontendApi:
    def __init__(self, service, validator):
        self.serv = service
        self.validator = validator
    

    def create_account(self, credentials):
        valid = self.validator.account_validator(credentials, new=True)

        if not valid:
            raise ValidationError("")

        return self.serv.create_account(credentials)


    def find_account(self, credentials):
        valid = self.validator.account_validator(credentials, new=False)

        if not valid:
            raise ValidationError("")

        login = credentials[0]

        return self.serv.find_account(login)


    def fund_account(self, user_account, funds_request):
        valid = self.validator.fund_validator(user_account.balance, funds_request)

        if not valid:
            raise ValidationError("")

        return self.serv.fund_account(user_account, funds_request)


    def create_portfolio(self, user_account, portfolio_name):
        valid = self.validator.portfolio_validator(user_account, portfolio_name, create = True)

        if not valid:
            raise ValidationError("")

        return self.serv.create_portfolio(user_account, portfolio_name)


    def remove_portfolio(self, user_account, portfolio_name):
        valid = self.validator.portfolio_validator(user_account, portfolio_name, create = False)

        if not valid:
            raise ValidationError("")

        return self.serv.remove_portfolio(user_account, portfolio_name)


    def execute_buy(self, user_account, portfolio, shares_requested):
        ticker = shares_requested[0]
        purchase = True

        valid = self.validator.stock_ticker_validator(portfolio, ticker, purchase)
        if not valid:
            raise ValidationError("")

        valid = self.validator.stock_quantity_validator(portfolio, shares_requested, purchase)
        if not valid:
            raise ValidationError("")

        valid = self.validator.sufficient_balance_validator(user_account.balance, shares_requested, purchase)
        if not valid:
            raise ValidationError("")

        return self.serv.execute_buy(user_account, portfolio, shares_requested)


    def execute_sell(self, user_account, portfolio, shares_requested):
        ticker = shares_requested[0]
        purchase = False

        valid = self.validator.stock_ticker_validator(portfolio, ticker, purchase)
        if not valid:
            raise ValidationError("")

        valid = self.validator.stock_quantity_validator(portfolio, shares_requested, purchase)
        if not valid:
            raise ValidationError("")

        valid = self.validator.sufficient_balance_validator(user_account.balance, shares_requested, purchase)
        if not valid:
            raise ValidationError("")

        return self.serv.execute_sell(user_account, portfolio, shares_requested)