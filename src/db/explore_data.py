from StockRegistry import StockRegistry
import pandas as pd
import glob, os





start_date = "2011-01-03"
end_date = "2017-11-10"
# 1. Set database dictionary - it will be created there!

os.chdir(r"..")

# 2. pcik name of dictionary !
registry = StockRegistry("stock_database.sqlite")

# Get 10 stocks
print(registry.getTop10("stocks"))
# Get 10 quotes
print(registry.getTop10("quotes"))

print('Num of rows stocks table:', registry.numOfRows("stocks"))
print('Num of rows quotes table:', registry.numOfRows("quotes"))

valid_ids = registry.getValidStockIds(start_date, end_date)
print(len(valid_ids))

validStockDict = dict()
for idx, stock_id in enumerate(valid_ids):
    validStockDict[idx] = stock_id
    
dailyReturnsMatrix = registry.gethDailyReturnsForRequestedStockIds( validStockDict, start_date, end_date)

print("Shape of returns matrix",dailyReturnsMatrix.shape)
registry.close()
