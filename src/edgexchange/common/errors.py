# PURPOSE: 
#   -DatabaseError provides a central database error abstraction
#   -Allows for exceptions to be re-raised as a general errortype for persistence layer
class DatabaseError(Exception):
    pass

# PURPOSE: 
#   -ValidationError provides a central validation error abstraction
#   -Allows the expression of invalid state as an error by raising this or a genuine error in validation layer
class ValidationError(Exception):
    pass

# PURPOSE: 
#   -ServiceError provides a central service error abstraction
#   -Allows for exceptions to be re-raised as a general errortype for service layer
class ServiceError(Exception):
    pass

# PURPOSE: 
#   -FetchingError provides a central external fetching error abstraction
#   -Allows for exceptions to be re-raised as a general errortype for any external fetches
class FetchingError(Exception):
    def __init__(self, message: str, ticker: str | None = None):
        super().__init__(message)
        self.ticker = ticker

# PURPOSE: 
#   -LiveCacheError provides a central live cache error abstraction
#   -Allows for exceptions to be re-raised as a general errortype for any live cache issue
class LiveCacheError(Exception):
    pass
