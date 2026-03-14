import os

from database import Database
from service import Service
from validator import Validator
from cli import Cli


class App:
    def __init__(self, database = None, service = None, validator = None, display = None):
        self.db = database
        self.serv = service
        self.val = validator
        self.display = display


    def init(self):
        db_dir = 'AppData'
        db_source = 'dummy.db'

        
        db_path = os.path.join(db_dir, db_source)

        if not os.path.exists(db_path):
           os.makedirs(db_dir)
        

        self.db = Database(db_path)
        self.serv = Service(self.db)
        self.val = Validator(self.serv)
        self.display = Cli(self.serv, self.val)

    def run(self):
        self.display.execute()