from .routes import connect
from common.errors import ValidationError


# PURPOSE:
class FrontendApi:
    def __init__(self, service, validator):
        self.serv = service
        self.validator = validator
    

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def link_routes(self):
        connect(self)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def resolve_uid(self, creds):
        return self.serv.resolve_uid(creds)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def create_account(self, credentials):
        valid = self.validator.account_validator(credentials, new=True)

        if not valid:
            raise ValidationError("")

        return self.serv.create_account(credentials)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def find_account(self, credentials):
        valid = self.validator.account_validator(credentials, new=False)

        if not valid:
            raise ValidationError("")

        login = credentials[0]

        return self.serv.find_account(login)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def fund_account(self, user_account, funds_request):
        valid = self.validator.fund_validator(funds_request)

        if not valid:
            raise ValidationError("")

        return self.serv.fund_account(user_account, funds_request)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def create_portfolio(self, user_account, portfolio_name):
        valid = self.validator.portfolio_validator(user_account, portfolio_name, create = True)

        if not valid:
            raise ValidationError("")

        return self.serv.create_portfolio(user_account, portfolio_name)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
    def remove_portfolio(self, user_account, portfolio_name):
        valid = self.validator.portfolio_validator(user_account, portfolio_name, create = False)

        if not valid:
            raise ValidationError("")

        return self.serv.remove_portfolio(user_account, portfolio_name)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
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


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    # RAISES:
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