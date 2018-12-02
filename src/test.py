from db.StockRegistry import StockRegistry
from clustering.Portfolio_Clustering import Portfolio_Cluster, getTopStockFromStockList
import sys
import scipy.stats as stat
sys.path.insert(0, '../clustering/Portfolio_Clustering')
from clustering import Portfolio_Clustering
import pandas as pd
import glob, os
from matplotlib import pyplot as pplot
import numpy as np





start_date = "2011-01-03"
end_date = "2017-11-10"

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

# -------------------------------------------------------- Check this !!! -----------------------------------------------------------------------------------------------------------
# TODO: stock_id 8193 corresponds to fmy.us.txt which doesn't actually contain all the data from 2011
print('first valid stock id:', validStockDict[0])
print('stock related to that stock id:', registry.getStockById(validStockDict[0]))
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

dailyReturnsMatrix = registry.gethDailyReturnsForRequestedStockIds( validStockDict, start_date, end_date)

print("Shape of returns matrix:", type(dailyReturnsMatrix), type(dailyReturnsMatrix[0][0]), dailyReturnsMatrix.shape)


n_clust = 10
cor_mat = Portfolio_Cluster.Correlation_Matrix(dailyReturnsMatrix)
dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)
link_mat = Portfolio_Cluster.ward_linkage(dist_mat)
cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)
clust_id_dict = Portfolio_Cluster.find_elements(cut_tree)
sharp_arr = Portfolio_Cluster.compute_sharp_ratios(dailyReturnsMatrix, 0.027)
print('sharp ratio size: %r; array: %r' % (sharp_arr.size, sharp_arr))

# The following code is to test the getTopStockFromStockList and getTopStockFromAllClusters methods
# print('top stock should be 3. The result is: ', getTopStockFromStockList([0,1,4], np.array([-1,3,5,12,1,0,8])))
# print('top stock by cluster should be [(2, 5), (3, 12)]. The result is: ', Portfolio_Cluster.getTopStockFromAllClusters({0: [0,1,2], 1: [3, 4]}, np.array([-1,3,5,12,1,0,8])))

# selected_stocks is a list of N stocks, each from one of N clusters, in a form (stock id, sharpe value)
selected_stocks = Portfolio_Cluster.getTopStockFromAllClusters(clust_id_dict, sharp_arr)
print('selected stocks (id, sharp):', selected_stocks)


registry.close()

# Open a PDF for plotting; units are inches by default
#pdf("/path/to/a/pdf/file.pdf", width=40, height=15)

# Do some plotting
#pplot.plot(cut_tree)

# Close the PDF file's associated graphics device (necessary to finalize the output)
#dev.off()

#print(cor_mat)
#print("\n")
#print(dist_mat)
#print("\n")
#print(link_mat)
#print("\n")
# print(cut_tree)

#print("\n")
# print(clust_id_dict.keys())
# print(clust_id_dict.values())
# print(clust_id_dict[0])
# print(clust_id_dict[4])
Portfolio_Cluster.save_dend(link_mat, 0)


#pplot.savefig('dendrogram.png')
Portfolio_Cluster.save_dend_cut(link_mat, n_clust=n_clust)
#pplot.show()
