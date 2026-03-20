import sqlite3 as sqlite
from sqlite3 import Error as SqliteError

# PURPOSE:
class DatabaseError(Exception):
    pass


# PURPOSE:
class Database:
    def __init__(self, source):
        self.source = source
        self.conn = sqlite.connect(source)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.build_database()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def build_database(self):
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
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_user(self, login : str) -> tuple:

        cursor = self.conn.cursor()

        pull_user = '''
            SELECT id, login, balance
            FROM users
            WHERE login = ?
        '''

        try:

            cursor.execute(pull_user, (login,))

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"pull_user failed: {e}") from e
        

        return cursor.fetchone()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_portfolios(self, user_id : int) -> list[tuple]:
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

        return cursor.fetchall()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_stocks(self, user_id : int) -> list[tuple]:
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

        return cursor.fetchall()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def update_funds(self, user_id : int, funds_request : float) -> None:
        cursor = self.conn.cursor()

        update_stock = '''
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?
        '''

        try:

            cursor.execute(update_stock, (funds_request, user_id))
            self.conn.commit()

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"update_funds failed: {e}") from e


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def resolve_credentials(self, credentials : tuple[str, str]):
        cursor = self.conn.cursor()

        resolve_id = '''
            SELECT id
            FROM users
            WHERE login = ? AND password = ?
        '''

        try:

            cursor.execute(resolve_id, credentials)

        except SqliteError as e:
            self.conn.rollback()
            raise DatabaseError(f"resolve_credentials failed: {e}") from e

        user_info = cursor.fetchone()

        if user_info == None:
            return None
        else:
            return user_info[0]