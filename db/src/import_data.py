
from StockRegistry import StockRegistry
import pandas as pd
import glob, os


# 1. Set database dictionary - it will be created there!

os.chdir(r"C:\Users\Kamil\Desktop\DTU sem 2\02807_Computational_Tools_for_Data_Science\project\db")

# 2. pcik name of dictionary !
registry = StockRegistry("stock_database.db")

# 3 import all stocks to the database:
# Set dir with Stocks
os.chdir("..\Data\Stocks")
stocks =  glob.glob("*.txt")
rows = []
for file in stocks:
    stock_short_name = file.split(".",1)[0]
    rows.append([stock_short_name,0])
registry.addManyStocks(rows)
    #print(stock_short_name)
    #registry.addStock(stock_short_name,0)
    

for file in stocks:
    stock_short_name = file.split(".",1)[0]
    stockId = registry.getStockId(stock_short_name)
    quotes = pd.read_csv(file,sep=",")
    quotes['stock_id']=stockId
    tuples = [tuple(x) for x in quotes.values]
    registry.addManyQuotes(tuples)


# 4 import all ETFs to the database: 
# Set dir with ETF
os.chdir("..\ETFs")
etfs =  glob.glob("*.txt")
rows = []
for file in etfs:
    etf_short_name = file.split(".",1)[0]
    rows.append([etf_short_name,1])
registry.addManyStocks(rows)

    
for file in etfs:
    etf_short_name = file.split(".",1)[0]
    stockId = registry.getStockId(etf_short_name)
    quotes = pd.read_csv(file,sep=",")
    quotes['stock_id']=stockId
    tuples = [tuple(x) for x in quotes.values]
    registry.addManyQuotes(tuples)
    
registry.close()

#for file in etfs:
 #   etf_short_name = file.split(".",1)[0]
 #   registry.updateStock(etf_short_name, 1)
