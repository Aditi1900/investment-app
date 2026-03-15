import sqlite3 as sqlite


# PURPOSE:
class Database:

    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
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

        cursor.executescript(create_user_table + create_portfolios_table + create_stocks_table)


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_user(self, login):
        u_id = self.resolve_user_id(login)

        cursor = self.conn.cursor()

        pull_user = '''
            SELECT id, login, password, balance
            FROM users
            WHERE id = ?
        '''

        cursor.execute(pull_user, (u_id,))

        return cursor.fetchone()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_portfolios(self, user_id):
        cursor = self.conn.cursor()

        pull_portfolios = f'''
            SELECT id, name
            FROM portfolios
            WHERE user_id = ?
        '''

        cursor.execute(pull_portfolios, (user_id,))

        return cursor.fetchall()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def pull_stocks(self, portfolio_id):
        cursor = self.conn.cursor()

        pull_stocks = f'''
            SELECT id, ticker, quantity
            FROM stocks
            WHERE portfolio_id = ?
        '''

        cursor.execute(pull_stocks, (portfolio_id,))

        return cursor.fetchall()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def insert_user(self, credentials):
        cursor = self.conn.cursor()

        insert_user = '''
            INSERT INTO users (login, password)
            VALUES (?, ?)
        '''

        cursor.execute(insert_user, credentials)
        self.conn.commit()

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def insert_portfolio(self, user_id, portfolioName):
        cursor = self.conn.cursor()

        insert_portfolio = '''
            INSERT INTO portfolios (user_id, name)
            VALUES (?, ?)
        '''

        cursor.execute(insert_portfolio, (user_id, portfolioName))
        self.conn.commit()

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def delete_portfolio(self, portfolio_id):
        cursor = self.conn.cursor()

        delete_portfolio = '''
            DELETE FROM portfolios
            WHERE id = ?
        '''

        cursor.execute(delete_portfolio, (portfolio_id,))
        self.conn.commit()



    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def insert_stock(self, portfolio_id, stock_dat):
        cursor = self.conn.cursor()

        insert_stock = '''
            INSERT INTO stocks (portfolio_id, ticker, quantity)
            VALUES (?, ?, ?)
        '''

        ticker, quantity = stock_dat

        cursor.execute(insert_stock, (portfolio_id, ticker, quantity))
        self.conn.commit()

        return cursor.lastrowid


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def delete_stock(self, stock_id):
        cursor = self.conn.cursor()

        delete_stock = '''
            DELETE FROM stocks 
            WHERE id = ?
        '''

        cursor.execute(delete_stock, (stock_id,))
        self.conn.commit()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def update_stock(self, stock_id, quantity):
        cursor = self.conn.cursor()

        update_stock = '''
            UPDATE stocks
            SET quantity = quantity + ?
            WHERE id = ?
        '''

        cursor.execute(update_stock, (quantity, stock_id))
        self.conn.commit()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def update_funds(self, user_id, funds):
        cursor = self.conn.cursor()

        update_stock = '''
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?
        '''

        cursor.execute(update_stock, (funds, user_id))
        self.conn.commit()


    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def resolve_user_id(self, login):
        cursor = self.conn.cursor()

        resolve_id = '''
            SELECT id
            FROM users
            WHERE login = ?
        '''

        key = (login,)

        cursor.execute(resolve_id, key)

        user_info = cursor.fetchone()

        if user_info == None:
            return None
        else:
            return user_info[0]