from pathlib import Path
from persistence_layer import Database
from service_layer import Service
from validation_layer import Validator
from interface_layer import *


# PURPOSE: 
#     -App provides initialization abstraction
#     -Allows for clean dependency injection and easy swaps between test mode
class App:
    def __init__(self, testing=False):
        self.db = None
        self.serv = None
        self.val = None
        self.display = None
        self.vis = None
        self.init(testing)


    # INPUT: 
    #     -testing(bool); app testing mode On or Off
    # OUTPUT: None
    # PRECONDITION: 
    #     -testing; is not None
    #     -App; all non static dependencies(db,serv,val,display,vis) are initialized to None
    # POSTCONDITION:
    #     -db; Database object constructed with established filepath
    #     -serv; Service object constructed with db injection
    #     -vis; Visualizer object constructed
    #     -val; Validator object constructed with serv injection
    #     -display; Cli object constructed with serv, val, vis injection
    # RAISES: None
    def init(self, testing : bool) -> None:
        if testing:
            db_path = ':memory:'
        else:
            db_path = self.establish_path('investment-app.db')
        
        
        self.db = Database(db_path)
        self.serv = Service(self.db)
        self.vis = Visualizer()
        self.val = Validator(self.serv)
        self.display = Cli(self.serv, self.val, self.vis)


    # INPUT:
    #     -db_source(str); database filename
    # OUTPUT:
    #     -db_path(Path); directory path of the database file
    # PRECONDITION:
    #     -db_source; has proper filename extension '.db' 
    # POSTCONDITION:
    #     -bootstrap.py parent directory; subdirectory 'app_data' exists
    #     -db_path; returned with relative path to database file
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
    #     -App; see init(), and establish_path() POSTCONDITION
    # POSTCONDITION: 
    #     -terminal; Cli starts execution on terminal
    #RAISES: None
    def run(self) -> None:
        self.display.execute()


if __name__ == "__main__" :
    app = App(testing = True)
    app.run()