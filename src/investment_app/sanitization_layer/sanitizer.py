# PURPOSE:
#   -Sanitizer provides a string input sanitization and conversion abstraction
#   -Provides methods to take a specific input the system needs and convert it to a non-malformed readable value
class Sanitizer:
    
    # INPUT:
    #   -login(str); raw user login input
    # OUTPUT:
    #   -login(str); sanitized user login
    # PRECONDITION: None
    # POSTCONDITION:
    #   -login; login is sanitized from basic malformed input
    # RAISES: None
    @staticmethod
    def sanitize_login(login : str) -> str:
        login = login.strip()
        return login


    # INPUT:
    #   -password(str); raw user password input
    # OUTPUT:
    #   -password(str); sanitized user password
    # PRECONDITION: None
    # POSTCONDITION:
    #   -password; password is sanitized from basic malformed input
    # RAISES: None
    @staticmethod
    def sanitize_password(password : str) -> str:
        return password


    # INPUT:
    #   -credentials(tuple[str,str]); a user login and password
    # OUTPUT:
    #   -credentials(tuple[str,str]); sanitized user login and password
    # PRECONDITION: None
    # POSTCONDITION:
    #   -credentials; see Sanitizer.sanitize_login() & Sanitizer.sanitize_password() POSTCONDITIONS
    # RAISES: None
    @staticmethod
    def sanitize_credentials(credentials : tuple[str, str]) -> tuple[str, str]:
        credentials = Sanitizer.sanitize_login(credentials[0]), Sanitizer.sanitize_password(credentials[1])
        return credentials


    # INPUT:
    #   -funds_request(str); a funds request input
    # OUTPUT:
    #   -funds_request(float); a floating point representation of funds_request, otherwise None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -funds_request; converted to a floating point number, if non numeric None
    # RAISES: None
    @staticmethod
    def sanitize_funds_request(funds_request : str) -> float | None:
        try:
            funds_request = float(funds_request)
        except Exception:
            funds_request = None

        return funds_request


    # INPUT:
    #   -portfolio_name(str); raw portfolio name input
    # OUTPUT:
    #   -portfolio_name(str); sanitized portfolio name
    # PRECONDITION: None
    # POSTCONDITION:
    #   -portfolio_name; portfolio name is sanitized from basic malformed input
    # RAISES: None
    @staticmethod
    def sanitize_portfolio_name(portfolio_name : str) -> str:
        portfolio_name = portfolio_name.strip()
        return portfolio_name


    # INPUT:
    #   -ticker(str); raw stock ticker input
    # OUTPUT:
    #   -ticker(str); sanitized ticker input
    # PRECONDITION: None
    # POSTCONDITION:
    #   -ticker; ticker is sanitized from basic malformed input
    # RAISES: None
    @staticmethod
    def sanitize_ticker(ticker : str) -> str:
        ticker = ticker.strip()
        return ticker


    # INPUT:
    #   -quantity(str); a quantity input
    # OUTPUT:
    #   -quantity(int); a integer representation of quantity, otherwise None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -quantity; converted to a integer, if non numeric None
    # RAISES: None
    @staticmethod
    def sanitize_quantity(quantity : str) -> int | None:
         try:
            quantity = int(quantity)
         except Exception:
            quantity = None

         return quantity

       
    # INPUT:
    #   -shares_request(tuple[str,str]); a ticker and quantity
    # OUTPUT:
    #   -shares_request(tuple[str,str]); sanitized ticker and quantity
    # PRECONDITION: None
    # POSTCONDITION:
    #   -shares_request; see Sanitizer.sanitize_ticker() & Sanitizer.sanitize_quantity() POSTCONDITIONS
    # RAISES: None
    @staticmethod
    def sanitize_shares_request(shares_request : tuple[str,str]) -> tuple[str, int | None]:
        shares_request = Sanitizer.sanitize_ticker(shares_request[0]), Sanitizer.sanitize_quantity(shares_request[1])
        return shares_request


    # INPUT:
    #   -selection(str); a selection input
    # OUTPUT:
    #   -selection(int); a integer representation of selection, otherwise None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -selection; converted to a integer, if non numeric -1
    # RAISES: None
    @staticmethod
    def sanitize_selection(selection : str) -> int | None:
         try:
            selection = int(selection)
         except Exception:
            selection = -1

         return selection
