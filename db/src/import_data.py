
from StockRegistry import StockRegistry
import pandas as pd
import glob, os
from time import time

start_date = "2011-01-03"
end_date = "2017-11-10"

# 1. Set database dictionary - it will be created there!

os.chdir(r"..")

# 2. pcik name of dictionary !
try:
    os.remove("stock_database.sqlite")
except:
    print('No previous database.')
print('Starting creation of new database: stock_database.sqlite ') 
start_time = time() 
registry = StockRegistry("stock_database.sqlite")
registry.createTables()

# 3 import all stocks to the database:
# Set dir with Stocks
os.chdir("data/Stocks")
stocks =  glob.glob("*.txt")
rows = []
for file in stocks:
    if os.path.getsize(file) > 0:
        stock_short_name = file.split(".",1)[0]
        rows.append([stock_short_name,0])
registry.addManyStocks(rows)
    #print(stock_short_name)
    #registry.addStock(stock_short_name,0)


for file in stocks:
    if os.path.getsize(file) > 0:
        stock_short_name = file.split(".",1)[0]
        stockId = registry.getStockId(stock_short_name)
        quotes = pd.read_csv(file,sep=",", usecols=[0, 4])
        quotes['stock_id']=stockId
        tuples = [tuple(x) for x in quotes.values]
        registry.addManyQuotes(tuples)


# 4 import all ETFs to the database:
# Set dir with ETF
os.chdir("../ETFs")
etfs =  glob.glob("*.txt")
rows = []
for file in etfs:
    if os.path.getsize(file) > 0:
        etf_short_name = file.split(".",1)[0]
        rows.append([etf_short_name,1])
registry.addManyStocks(rows)


for file in etfs:
    if os.path.getsize(file) > 0:
        etf_short_name = file.split(".",1)[0]
        stockId = registry.getStockId(etf_short_name)
        quotes = pd.read_csv(file,sep=",", usecols=[0, 4])
        quotes['stock_id']=stockId
        tuples = [tuple(x) for x in quotes.values]
        registry.addManyQuotes(tuples)

# Create index for date
registry.createIndexForDateQueries()
registry.createForeignKeyIndexOnStockId()
registry.addDailyStockReturnColumn()
import_time = time()
print("Import time: " + str(import_time - start_time))
print("Starting daily return calculation:")
registry.calculateDailyStockReturnForStocksFromTheTimeRange(start_date,end_date)
calculation_time = time()
print("Calculation time: " + str(calculation_time-import_time))
print("Starting index creation")
registry.createIndexOnDailyReturnsTempTable()
print("Starting daily returns insertion ")
registry.inputDailyStockReturn()
insertion_time = time()
print("Insertion time: " + str(insertion_time-calculation_time))
print("Total process done within time of: "+str(insertion_time-start_time) )

#stock_numbers = registry.calculateDailyStockReturnForStocksFromTheTimeRange(start_date,end_date)
#no_of_stock_to_update = len(stock_numbers)
#print("Statring daily return insertion of:" + str(no_of_stock_to_update) +' different stock daily returns')

#for counter, idx in enumerate(stock_numbers,start = 1):
#    registry.inputDailyStockReturn(idx)
#    print("Done stock_id: idx")
registry.close()

#for file in etfs:
 #   etf_short_name = file.split(".",1)[0]
 #   registry.updateStock(etf_short_name, 1)
