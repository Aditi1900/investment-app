
from domain_models import portfolio


class Sanitizer:

    @staticmethod
    def sanitize_login(login : str) -> str:
        login = login.strip()
        return login


    @staticmethod
    def sanitize_password(password : str) -> str:
        return password

    @staticmethod
    def sanitize_credentials(self, credentials : tuple[str, str]) -> tuple[str, str]:
        credentials = self.sanitize_login(credentials[0]), self.sanitize_password(credentials[1])
        return credentials

    @staticmethod
    def sanitize_funds_request(funds_request : str) -> float | None:
        try:
            funds_request = float(funds_request)
        except Exception:
            funds_request = None

        return funds_request

    @staticmethod
    def sanitize_portfolio_name(portfolio_name : str) -> str:
        portfolio_name.strip()
        return portfolio_name

    @staticmethod
    def sanitize_ticker(ticker : str) -> str:
        ticker = ticker.strip()
        return ticker

    @staticmethod
    def sanitize_quantity(quantity : str) -> int:
         try:
            quantity = int(quantity)
         except Exception:
            quantity = None

         return quantity

       

    @staticmethod
    def sanitize_shares_request(self, shares_request : tuple[str,str]) -> tuple[str, str]:
        shares_request = self.sanitize_ticker(shares_request[0]), self.sanitize_quantity(shares_request[1])
        return shares_request


