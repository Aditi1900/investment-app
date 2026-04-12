import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..integration_layer import FrontendApi, router


# PURPOSE: 
#   -Frontend provides a serving abstraction
#   -Allows for frontend connection to the system through FrontendApi routes
class Frontend:
    def __init__(self, service, sanitizer, validator):

        origins = ["http://localhost:3000"]

        FrontendApi(service, sanitizer, validator).link_routes()

        self.app = FastAPI()
        self.app.add_middleware(CORSMiddleware, allow_origins = origins, allow_credentials = True, allow_methods = ['*'], allow_headers = ['*'])
        self.app.include_router(router)

    
    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -self.app; FastAPI instance configured with CORS middleware and routes
    # POSTCONDITION:
    #   -self.app; served on 0.0.0.0:8000 until server is stopped
    # RAISES: None
    def execute(self) -> None:
        uvicorn.run(self.app, host="0.0.0.0", port=8000)