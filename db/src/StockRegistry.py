import sqlite3
import os

class StockRegistry:
    # Initialize the StockRegistry. The name of the database file used for
    # this instance is given as a parameter. This database will in some
    # cases be pre populated, and in some cases empty.
    # You do not need to change this function.
    def __init__(self, databaseName):
        self.db = sqlite3.connect(databaseName)
        self.c = self.db.cursor()

    # Clean up the database. You do not need to change this function.
    def close(self):
        self.db.close()

    # This function should create two tables stocks and quotes.
    # You can assume the tables do not exist.
    def createTables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS stocks
            ( stock_id INTEGER NOT NULL, name TEXT NOT NULL UNIQUE, is_etf INTEGER NOT NULL, PRIMARY KEY(stock_id) )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS quotes
            ( quote_id INTEGER NOT NULL UNIQUE, date TEXT NOT NULL, close REAL NOT NULL, stock_id NUMERIC NOT NULL, FOREIGN KEY(stock_id) REFERENCES stocks(stock_id), PRIMARY KEY(quote_id) )''')
        self.db.commit()

    # Add a row to the models table.
    def addStock(self, stockName, isETF):
        self.c.execute('INSERT INTO stocks( name, is_etf) VALUES (?,?)', [stockName,isETF])
        self.db.commit()

    def updateStock(self, stockName, isETF):
        self.c.execute('UPDATE stocks set is_etf=(?) where name=(?)',[isETF,stockName])
        self.db.commit()

    def addManyStocks(self, rows):
        try:
            self.c.executemany('INSERT INTO stocks( name, is_etf) VALUES (?,?)', rows)
            self.db.commit()
        except sqlite3.IntegrityError as ie:
            print ('addManyStocks ie:'+str( ie))
        except sqlite3.Error as er:
            print ('addManyStocks er:'+str( er))
            self.db.close()

    def addManyQuotes(self, rows):
        try:
            self.c.executemany('INSERT INTO quotes( date, close, stock_id) VALUES (?,?,?)', rows)
            self.db.commit()
        except sqlite3.Error as er:
            print ('addManyQuotes er:'+str( er))
            self.db.close()
    # Add a row to the registration table.
    def addQuote(self, date, openValue, high, low, close, volumne, openInd, stockId):
        self.c.execute('INSERT INTO quotes VALUES (?,?,?)', [date, close, stockId])
        self.db.commit()

    # Delete the row with the given carId from the registration table.
    def getStockId(self, stockName):
        return self.c.execute('Select stock_id FROM stocks WHERE name = (?)', [stockName]).fetchone()[0]

    def getTop10(self, table_name):
        return self.c.execute('SELECT * FROM %s LIMIT 10' % table_name).fetchall()

    def numOfRows(self, table_name):
        return self.c.execute('SELECT COUNT(*) FROM %s' % table_name).fetchone()

    def getValidStockIds(self, first_date, last_date):
        lower_bound_ids = set([tuple[0] for tuple in self.c.execute('SELECT stock_id FROM quotes WHERE date=?', [first_date]).fetchall()])
        upper_bound_ids = set([tuple[0] for tuple in self.c.execute('SELECT stock_id FROM quotes WHERE date=?', [last_date]).fetchall()])

        return lower_bound_ids.intersection(upper_bound_ids)


    # Populate the registration and models tables with meaningful data.
    # Ie. carIds must be unique, for any modelId in registration there
    # should be a corresponding row in models, etc. You must add at least
    # 10 rows to each of the two tables.
    #def addManyStocks(self, stocks):
        #pass
        #c.executemany('INSERT INTO models VALUES (?,?,?)', models)
        #c.executemany('INSERT INTO registrations VALUES (?,?,?,?)', registrations)
        #self.db.commit()

    def deleteDatabase(self, databaseName):
        os.remove(databaseName)
