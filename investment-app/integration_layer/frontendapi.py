from .routes import connect
from common.errors import ValidationError


# PURPOSE:
#   -FrontendApi provides a user operation abstraction
#   -This abstraction is provided to enforce function contracts on POST or GET request
class FrontendApi:
    def __init__(self, service, sanitizer, validator):
        self.serv = service
        self.validator = validator
        self.san = sanitizer
    

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective .routes connect() fields
    def link_routes(self):
        connect(self)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION/RAISES: see respective Service.resolve_uid() fields
    def resolve_uid(self, login):
        login = self.san.sanitize_login(login)
        u_id = self.serv.resolve_uid(login)
        return u_id 


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.create_account() fields
    # RAISES:
    #   -ValidationError; see Validator.account_validator() POSTCONDITION (new=True)
    def create_account(self, credentials):
        credentials = self.san.sanitize_credentials(credentials)

        result = self.validator.account_validator(credentials, new=True)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.create_account(credentials)


    # INPUT:
    #   -credentials(tuple[str,str]); user login and password
    # OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.find_account() fields
    # RAISES:
    #   -ValidationError; see Validator.account_validator() POSTCONDITION (new=False)
    def find_account(self, credentials):
        credentials = self.san.sanitize_credentials(credentials)

        result = self.validator.account_validator(credentials, new=False)
        if not result.valid:
            raise ValidationError(result.reason)

        login = credentials[0]

        return self.serv.find_account(login)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.fund_account() fields
    # RAISES:
    #   -ValidationError; see Validator.fund_validator() POSTCONDITION
    def fund_account(self, user_account, funds_request):
        funds_request = self.san.sanitize_funds_request(funds_request)

        result = self.validator.fund_validator(funds_request)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.fund_account(user_account, funds_request)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.create_portfolio() fields
    # RAISES:
    #   -ValidationError; see Validator.portfolio_validator() POSTCONDITION (create=True)
    def create_portfolio(self, user_account, portfolio_name):
        portfolio_name = self.san.sanitize_portfolio_name(portfolio_name)

        result = self.validator.portfolio_validator(user_account, portfolio_name, create=True)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.create_portfolio(user_account, portfolio_name)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.remove_portfolio() fields
    # RAISES:
    #   -ValidationError; see Validator.portfolio_validator() POSTCONDITION (create=False)
    def remove_portfolio(self, user_account, portfolio_name):
        portfolio_name = self.san.sanitize_portfolio_name(portfolio_name)

        result = self.validator.portfolio_validator(user_account, portfolio_name, create=False)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.remove_portfolio(user_account, portfolio_name)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.execute_buy() fields
    # RAISES:
    #   -ValidationError; see Validator.shares_request_validator() POSTCONDITION (purchase=True)
    def execute_buy(self, user_account, portfolio, shares_request):
        shares_request = self.san.sanitize_shares_request(shares_request)

        result = self.validator.shares_request_validator(portfolio, shares_request, user_account.balance, purchase=True)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.execute_buy(user_account, portfolio, shares_request)


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective Service.execute_sell() fields
    # RAISES:
    #   -ValidationError; see Validator.shares_request_validator() POSTCONDITION (purchase=False)
    def execute_sell(self, user_account, portfolio, shares_request):
        shares_request = self.san.sanitize_shares_request(shares_request)

        result = self.validator.shares_request_validator(portfolio, shares_request, user_account.balance, purchase=False)
        if not result.valid:
            raise ValidationError(result.reason)

        return self.serv.execute_sell(user_account, portfolio, shares_request)