import sqlite3 as sqlite
from sqlite3 import Error as SqliteError
from common.errors import DatabaseError



# PURPOSE: 
#   -Database provides a SQLite database operation abstraction
#   -Allows for seperation of database specific operations from buisness logic
class Database:
    def __init__(self, source):
        self.source = source
        self.conn = sqlite.connect(source)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.build_database()


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -Database; source attached to filepath, connection to source established, foreign keys enabled
    # POSTCONDITION:
    #   -database; users, portfolios, and stocks tables exist and are properly linked
    # RAISES:
    #   -DatabaseError; SqliteError occurs during table creation
    def build_database(self) -> None:
        cursor = self.conn.cursor()

        create_user_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0
            );
        '''

        create_portfolios_table = '''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,

                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

                UNIQUE(user_id, name)
            );
        '''

        create_stocks_table = '''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY,
                portfolio_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,

                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,

                UNIQUE(portfolio_id, ticker)
            );
        '''

        try:

            cursor.executescript(create_user_table + create_portfolios_table + create_stocks_table)

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"build_database failed: {e}") from e


    # INPUT:
    #   -login(str); user login 
    # OUTPUT:
    #   -user_data(tuple[int,str,float]); user data from database id, login, password, balance or None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -user_data; database information related to user with respective login is retrieved, None otherwise
    # RAISES:
    #   -DatabaseError; SqliteError occurs during selection 
    def pull_user(self, login : str) -> tuple[int, str, float] | None:

        cursor = self.conn.cursor()

        pull_user = '''
            SELECT id, login, password, balance
            FROM users
            WHERE login = ?
        '''

        try:

            cursor.execute(pull_user, (login,))

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"pull_user failed: {e}") from e
        
        user_data = cursor.fetchone()

        return user_data


    # INPUT:
    #   -user_id(int); user id number in database
    # OUTPUT:
    #   -user_portfolios(list[tuple[int,str]]); list of all portfolios the user has
    # PRECONDITION:
    #   -user_id; exists in database  
    # POSTCONDITION:
    #   -user_portfolios; database information related to all user portfolios is retrieved
    # RAISES:
    #   -DatabaseError; SqliteError occurs during selection
    def pull_portfolios(self, user_id : int) -> list[tuple[int, str]]:
        cursor = self.conn.cursor()

        pull_portfolios = f'''
            SELECT id, name
            FROM portfolios
            WHERE user_id = ?
        '''

        try:

            cursor.execute(pull_portfolios, (user_id,))

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"pull_portfolios failed: {e}") from e

        user_portfolios = cursor.fetchall()

        return user_portfolios


    # INPUT:
    #   -user_id(int); user id number in database 
    # OUTPUT:
    #   -user_stocks(list[tuple[int,int,str,int]]); list of all users owned stocks across all portfolios
    # PRECONDITION:
    #   -user_id; exists in database
    # POSTCONDITION:
    #   -user_stocks; database information for all user owned stocks is retrieved
    # RAISES:
    #   -DatabaseError; SqliteError occurs during selection
    def pull_stocks(self, user_id : int) -> list[tuple[int, int, str, int]]:
        cursor = self.conn.cursor()

        pull_stocks = f'''
            SELECT s.portfolio_id, s.id, s.ticker, s.quantity
            FROM stocks s
            JOIN portfolios p ON s.portfolio_id = p.id
            WHERE p.user_id = ?
        '''

        try:

            cursor.execute(pull_stocks, (user_id,))

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"pull_stocks failed: {e}") from e

        user_stocks = cursor.fetchall()

        return user_stocks


    # INPUT:
    #   -credentials(tuple[str,str]); new user login and password
    # OUTPUT:
    #   -u_id(int); the database primary key for the new user
    # PRECONDITION:
    #   -credentials; see Validator.account_validator() POSTCONDITION
    # POSTCONDITION:
    #   -database; user credentials are used to create a new user entry in database
    #   -u_id; a user primary key from the database is generated and returned
    # RAISES:
    #   -DatabaseError; SqliteError occurs on insert
    def insert_user(self, credentials : tuple[str, str]) -> int:
        cursor = self.conn.cursor()

        insert_user = '''
            INSERT INTO users (login, password)
            VALUES (?, ?)
        '''

        try:

            cursor.execute(insert_user, credentials)
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"insert_user failed: {e}") from e

        u_id = cursor.lastrowid

        return u_id


    # INPUT:
    #   -user_id(int); user id number in database
    #   -portfolio_name(str); name of new portfolio  
    # OUTPUT:
    #   -p_id(int); the database primary key for the new portfolio
    # PRECONDITION:
    #   -user_id; user id exists in the database
    #   -portfolio_name; see Validator.portfolio_validator() POSTCONDITION
    # POSTCONDITION:
    #   -database; portfolio name and user id are used to create a new portfolio entry
    #   -p_id; a portfolio primary key from database is generated and returned
    # RAISES:
    #   -DatabaseError; SqliteError occurs during insertion
    def insert_portfolio(self, user_id : int, portfolio_name : str) -> int:
        cursor = self.conn.cursor()

        insert_portfolio = '''
            INSERT INTO portfolios (user_id, name)
            VALUES (?, ?)
        '''

        try:

            cursor.execute(insert_portfolio, (user_id, portfolio_name))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"insert_portfolio failed: {e}") from e

        p_id = cursor.lastrowid

        return p_id 


    # INPUT:
    #   -portfolio_id(int); portfolio id number in database
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_id; portfolio id exists in the database
    # POSTCONDITION:
    #   -database; portfolio is deleted, deletes CASCADE to stocks, total database removal
    # RAISES:
    #   -DatabaseError; SqliteError occurs during delete
    def delete_portfolio(self, portfolio_id : int) -> None:
        cursor = self.conn.cursor()

        delete_portfolio = '''
            DELETE FROM portfolios
            WHERE id = ?
        '''

        try:

            cursor.execute(delete_portfolio, (portfolio_id,))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"delete_portfolio failed: {e}") from e



    # INPUT:
    #   -portfolio_id(int); portfolio id number in database
    #   -shares_requested(tuple[str,int]); ticker and quantity of shares requested  
    # OUTPUT:
    #   -s_id(int); the database primary key for the new stock
    # PRECONDITION:
    #   -portfolio_id; portfolio id exists in the database
    #   -shares_requested; see Validator.stock_ticker_validator() & Validator.stock_quantity_validator() POSTCONDITIONS
    # POSTCONDITION:
    #   -database; stock ticker, quantity and portfolio id are used to create a new stock entry
    #   -s_id; a stock primary key from database is generated and returned
    # RAISES:
    #   -DatabaseError; SqliteError occurs during insertion
    def insert_stock(self, portfolio_id : int, shares_requested : tuple[str, int]) -> int:
        cursor = self.conn.cursor()

        insert_stock = '''
            INSERT INTO stocks (portfolio_id, ticker, quantity)
            VALUES (?, ?, ?)
        '''

        ticker, quantity = shares_requested

        try:

            cursor.execute(insert_stock, (portfolio_id, ticker, quantity))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"insert_stock failed: {e}") from e

        s_id = cursor.lastrowid

        return s_id 


    # INPUT:
    #   -stock_id(int); stock id number in database
    # OUTPUT: None
    # PRECONDITION:
    #   -stock_id; stock id exists in the database
    # POSTCONDITION:
    #   -database; stock is deleted, total database removal
    # RAISES:
    #   -DatabaseError; SqliteError occurs during delete
    def delete_stock(self, stock_id : int) -> None:
        cursor = self.conn.cursor()

        delete_stock = '''
            DELETE FROM stocks 
            WHERE id = ?
        '''

        try:

            cursor.execute(delete_stock, (stock_id,))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"delete_stock failed: {e}") from e


    # INPUT:
    #   -stock_id(int); stock id number in database 
    #   -quantity(int); quantity of stocks to add or remove 
    # OUTPUT: None
    # PRECONDITION:
    #   -stock_id; stock id exists in the database
    #   -quantity; != 0, result of update cannot reduce stock below 0
    # POSTCONDITION:
    #   -database; stock information is properly updated
    # RAISES:
    #   -DatabaseError; SqliteError occurs during update
    def update_stock(self, stock_id : int, quantity : int) -> None:
        cursor = self.conn.cursor()

        update_stock = '''
            UPDATE stocks
            SET quantity = quantity + ?
            WHERE id = ?
        '''

        try:

            cursor.execute(update_stock, (quantity, stock_id))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"update_stock failed: {e}") from e


    # INPUT:
    #   -user_id(int); user id number in database
    #   -funds_request(float); amount to be added or removed from balance
    # OUTPUT: None
    # PRECONDITION:
    #   -user_id; user id exists in database
    #   -funds_request; != 0, result of update cannot reduce balance below 0 
    # POSTCONDITION:
    #   -database; users balance is updated
    # RAISES:
    #   -DatabaseError; SqliteError occurs during update
    def update_funds(self, user_id : int, funds_request : float) -> None:
        cursor = self.conn.cursor()

        update_funds = '''
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?
        '''

        try:

            cursor.execute(update_funds, (funds_request, user_id))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"update_funds failed: {e}") from e


    