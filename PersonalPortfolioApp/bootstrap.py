import os

from persistence_layer import Database
from service_layer import Service
from validation_layer import Validator
from interface_layer import *


# PURPOSE:
class App:

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def __init__(self, testing=False):
        self.db = None
        self.serv = None
        self.val = None
        self.display = None
        self.vis = None
        self.init(testing=testing)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def init(self, testing=False):

        db_dir = 'AppData'
        db_source = 'app_data.db'

        db_path = os.path.join(db_dir, db_source)

        os.makedirs(db_dir, exist_ok=True)


        if testing:
            self.db = Database(':memory:')
            self.serv = Service(self.db)
            self.vis = Visualizer()
            self.val = Validator(self.serv)
            self.display = Cli(self.serv, self.val, self.vis)
            return
        

        self.db = Database(db_path)
        self.serv = Service(self.db)
        self.vis = Visualizer()
        self.val = Validator(self.serv)
        self.display = Cli(self.serv, self.val, self.vis)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def run(self):
        self.display.execute()


if __name__ == "__main__" :
    app = App(testing = True)
    app.run()