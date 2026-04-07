from pathlib import Path

from interface_layer import Cli, Visualizer, Frontend
from sanitization_layer import Sanitizer
from validation_layer import Validator
from service_layer import Service
from persistence_layer import Database


# PURPOSE:
#	-App provides initialization abstraction
#	-Allows for clean dependency injection and easy swaps between test mode and display type
class App:
    def __init__(self, testing=False, frontend=True):
        self.init(testing, frontend)


    # INPUT:
    #	-testing(bool); whether to run in test mode
    #	-frontend(bool); whether to run FastAPI frontend or CLI
    # OUTPUT: None
    # PRECONDITION:
    #	-testing; is True or False
    #	-frontend; is True or False
    # POSTCONDITION:
    #   -self.san; Sanitizer constructed
    #	-self.db; Database constructed with resolved db_path
    #	-self.serv; Service constructed with self.db injection
    #	-self.val; Validator constructed with self.serv injection
    #	-frontend=True; self.display is Frontend with serv, san, val injection
    #	-frontend=False; self.vis is Visualizer; self.display is Cli with serv, san, val, vis injection
    # RAISES: None
    def init(self, testing : bool, frontend : bool) -> None:
        if testing:
            db_path = ':memory:'
        else:
            db_path = self.establish_path('investment-app.db')

        self.san = Sanitizer()
        self.db = Database(db_path)
        self.serv = Service(self.db)
        self.val = Validator(self.serv)

        if frontend:
            self.display = Frontend(self.serv, self.san, self.val)
        else:
            self.vis = Visualizer()
            self.display = Cli(self.serv, self.san, self.val, self.vis)


    # INPUT:
    #	-db_source(str); database filename
    # OUTPUT:
    #	-db_path(Path); full path to database file
    # PRECONDITION:
    #	-db_source; non-empty string ending with '.db'
    # POSTCONDITION:
    #	-'app_data/'; subdirectory exists relative to __file__
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
    #	-self.display; initialized via init()
    # POSTCONDITION:
    #	-frontend=True; uvicorn serves app on 0.0.0.0:8000
    #	-frontend=False; Cli drives execution on terminal
    # RAISES: None
    def run(self) -> None:
        self.display.execute()
    

if __name__ == "__main__" :
    investment_app = App(testing = True, frontend = False)
    investment_app.run()