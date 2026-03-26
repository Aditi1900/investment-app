import uvicorn

from fastapi import FastAPI
from integration_layer import FrontendApi, router, init

class Frontend:
    def __init__(self, service, validator):
        self.api = FrontendApi(service, validator)
        self.app = FastAPI()
        init(self.api)
        self.app.include_router(router)

    def execute(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)