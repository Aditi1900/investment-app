import uvicorn

from pathlib import Path
from fastapi import FastAPI
from persistence_layer import Database
from service_layer import Service
from validation_layer import Validator
from interface_layer import Cli, Visualizer
from integration_layer import FrontendApi, router, init


# PURPOSE:
#	-App provides initialization abstraction
#	-Allows for clean dependency injection and easy swaps between test mode and display type
class App:
    def __init__(self, testing=False, frontend=True):
        self.frontend = frontend
        self.init(testing, frontend)


    # INPUT:
	#	-testing(bool); whether to run in test mode
	#	-frontend(bool); whether to run FastAPI frontend or CLI
	# OUTPUT: None
	# PRECONDITION:
	#	-testing; is True or False
	#	-frontend; is True or False
	# POSTCONDITION:
	#	-self.db; Database constructed with resolved db_path
	#	-self.serv; Service constructed with self.db injection
	#	-self.val; Validator constructed with self.serv injection
	#	-frontend=True; self.display is FrontendApi; self.app is FastAPI with router mounted
	#	-frontend=False; self.vis is Visualizer; self.display is Cli with serv, val, vis injection
	# RAISES: None
    def init(self, testing : bool, frontend : bool) -> None:
        if testing:
            db_path = ':memory:'
        else:
            db_path = self.establish_path('investment-app.db')
        
        
        self.db = Database(db_path)
        self.serv = Service(self.db)
        self.val = Validator(self.serv)

        if frontend:
            self.display = FrontendApi(self.serv, self.val)
            self.app = FastAPI()
            init(self.display)
            self.app.include_router(router)
        else:
            self.vis = Visualizer()
            self.display = Cli(self.serv, self.val, self.vis)


    # INPUT:
	#	-db_source(str); database filename
	# OUTPUT:
	#	-db_path(Path); full path to database file
	# PRECONDITION:
	#	-db_source; ends with '.db'
	# POSTCONDITION:
	#	-'app_data/'; subdirectory exists relative to bootstrap.py
	#	-db_path; points to db_source inside 'app_data/'
	# RAISES: None
    def establish_path(self, db_source : str) -> Path:
        base_dir = Path(__file__).parent

        db_dir = base_dir / 'app_data'

        db_dir.mkdir(exist_ok = True)

        db_path = db_dir / db_source

        return db_path 


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -App; see init() and establish_path() POSTCONDITION
    # POSTCONDITION:
    #   -frontend=True; uvicorn serves app on 0.0.0.0:8000
    #   -frontend=False; Cli starts execution on terminal
    # RAISES: None
    def run(self) -> None:
        if self.frontend:
            uvicorn.run(self.app, host="0.0.0.0", port=8000)
        else:
            self.display.execute()


if __name__ == "__main__" :
    investment_app = App(testing = True, frontend = False)
    investment_app.run()