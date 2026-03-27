import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from integration_layer import FrontendApi, router, init


# PURPOSE: 
#   -Frontend provides a serving abstraction
#   -Allows for frontend connection to the system through FrontendApi routes
class Frontend:
    def __init__(self, service, validator):

        origins = ["http://localhost:3000"]

        init(FrontendApi(service, validator))

        self.app = FastAPI()
        self.app.add_middleware(CORSMiddleware, allow_origins = origins, allow_credentials = True, allow_methods = ['*'], allow_headers = ['*'])
        self.app.include_router(router)


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -FrontendApi; is initialized with proper dependencies
    #   -self.app; FastApi instance is created, CORS exceptions are included for browser compatibility, and routes are established
    # POSTCONDITION:
    #   -Frontend; frontend was served on port 8000 on local network for duration of server running
    # RAISES: None
    def execute(self) -> None:
        uvicorn.run(self.app, host="0.0.0.0", port=8000)