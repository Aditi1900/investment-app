import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from integration_layer import FrontendApi, router, init

class Frontend:
    def __init__(self, service, validator):

        origins = ["http://localhost:3000"]

        self.api = FrontendApi(service, validator)
        self.app = FastAPI()
        self.app.add_middleware(CORSMiddleware, allow_origins = origins, allow_methods = ['*'], allow_headers = ['*'])
        init(self.api)
        self.app.include_router(router)

    def execute(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)