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
            ( quote_id INTEGER NOT NULL UNIQUE, date DATE NOT NULL, close REAL NOT NULL, stock_id NUMERIC NOT NULL, FOREIGN KEY(stock_id) REFERENCES stocks(stock_id), PRIMARY KEY(quote_id) )''')
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


    # This function should create an index that ensures
    # queries considering date will execute fast
    def createIndexForDateQueries(self):
        self.c.execute("CREATE INDEX dateId on quotes(date)")
        
    def createForeignKeyIndexOnStockId(self):
        self.c.execute("CREATE INDEX stock_idx on quotes(stock_id)")
        
    def addDailyStockReturnColumn(self):
        self.c.execute("ALTER TABLE quotes ADD COLUMN daily_return REAL")
        
    def calculateDailyStockReturn(self, stock_id):
        return self.c.execute('''select  (q1.close - q2.close) / q2.close as ret_value ,q1.stock_id, q1.date
                       from quotes q1 
                       left join quotes q2 on (q1.stock_id = q2.stock_id and  q1.quote_id = q2.quote_id+1) 
                       where q1.stock_id = ? and q1.date between ? and ?
                       order by q1.date''', [stock_id,'2011-01-03','2017-11-10']).fetchall()
    
    def inputDailyStockReturn(self):
        self.c.executemany('''UPDATE quotes 
                       SET daily_return = (SELECT DailyReturns.ret_value
                                           FROM DailyReturns
                                           WHERE DailyReturns.stock_id = quotes.stock_id
                                           AND DailyReturns.date = quotes.date
                                           )
                       WHERE EXISTS (
                                       SELECT * 
                                       FROM DailyReturns
                                       WHERE DailyReturns.stock_id = quotes.stock_id
                                       AND DailyReturns.date = quotes.date
                                      )''')
        self.db.commit()
        self.c.execute('''DROP TABLE IF EXISTS DailyReturns''')
        self.db.commit()

    def calculateDailyStockReturnForStocksFromTheTimeRange(self, first_date, last_date ):
        data_to_update = self.c.execute('''
        CREATE TEMPORARY TABLE DailyReturns AS
        WITH VALID_STOCK_IDS AS (
                                    select stock_id from quotes
                                    where quotes.date = ?
                                    intersect
                                    select stock_id from quotes
                                    where quotes.date = ?
                                )
        
        select (q1.close - q2.close) / q2.close as ret_value ,q1.stock_id, q1.date 
        from VALID_STOCK_IDS vsi
        left join quotes q1 on vsi.stock_id = q1.stock_id
        left join quotes q2 on (q1.stock_id = q2.stock_id and  q1.quote_id = q2.quote_id+1)
        where q1.date between ? and ?
        order by q1.date
                       ''', [first_date,last_date,first_date,last_date]).fetchall()
        return data_to_update
    
    def executeCommitStatement(self):
        self.db.commit()
        