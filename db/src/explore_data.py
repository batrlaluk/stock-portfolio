from StockRegistry import StockRegistry
import pandas as pd
import glob, os


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

registry.close()
