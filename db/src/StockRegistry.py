import sqlite3
import os

class StockRegistry:
    # Initialize the CarRegistry. The name of the database file used for
    # this instance is given as a parameter. This database will in some
    # cases be pre populated, and in some cases empty.
    # You do not need to change this function.
    def __init__(self, databaseName):
        self.db = sqlite3.connect(databaseName)
    
    # Clean up the database. You do not need to change this function.
    def close(self):
        self.db.close()
        
    
    # Add a row to the models table.
    def addStock(self, stockName, isETF):
        c = self.db.cursor()
        c.execute('INSERT INTO stocks( name, is_etf) VALUES (?,?)', [stockName,isETF])
        self.db.commit()
        
    def updateStock(self, stockName, isETF):
        c = self.db.cursor()
        c.execute('UPDATE stocks set is_etf=(?) where name=(?)',[isETF,stockName])
        self.db.commit()
        
    def addManyStocks(self, rows):
        try:
            c = self.db.cursor()
            c.executemany('INSERT INTO stocks( name, is_etf) VALUES (?,?)', rows)
            self.db.commit()
        except sqlite3.IntegrityError as ie:
            print ('addManyStocks ie:'+str( ie))
        except sqlite3.Error as er:
            print ('addManyStocks er:'+str( er))
            self.db.close()
        
    def addManyQuotes(self, rows):
        try:
            c = self.db.cursor()
            c.executemany('INSERT INTO quotes( date, open, high, low, close, volume, open_int, stock_id) VALUES (?,?,?,?,?,?,?,?)', rows)
            self.db.commit()
        except sqlite3.Error as er:
            print ('addManyQuotes er:'+str( er))
            self.db.close()
    # Add a row to the registration table.
    def addQuote(self, date, openValue,high,low,close, volumne, openInd, stockId):
        c = self.db.cursor()
        c.execute('INSERT INTO quotes VALUES (?,?,?,?,?,?,?,?)', [date,openValue,high,low,close, volumne, openInd, stockId])
        self.db.commit()
    
    # Delete the row with the given carId from the registration table.
    def getStockId(self, stockName):
        c = self.db.cursor()
        return c.execute('Select stock_id FROM stocks WHERE name = (?)', [stockName]).fetchone()[0]
    
    def getTop10(self, table_name):
        c = self.db.cursor()
        return c.execute('Select top 10 * FROM (?)', [table_name]).fetchall()


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
    