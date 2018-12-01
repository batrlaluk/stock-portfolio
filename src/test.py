from db.StockRegistry import StockRegistry
from clustering.Portfolio_Clustering import Portfolio_Cluster
import sys
sys.path.insert(0, '../clustering/Portfolio_Clustering')
from clustering import Portfolio_Clustering
import pandas as pd
import glob, os
from matplotlib import pyplot as pplot





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

dailyReturnsMatrix = registry.gethDailyReturnsForRequestedStockIds( validStockDict, start_date, end_date)

print("Shape of returns matrix",dailyReturnsMatrix.shape)
registry.close()


n_clust = 5
cor_mat = Portfolio_Cluster.Correlation_Matrix(dailyReturnsMatrix)
dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)

link_mat = Portfolio_Cluster.link(dist_mat)
cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)



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
print(cut_tree)

#print("\n")
#print(clust_id_dict.keys())
#print(clust_id_dict.values())
#print(clust_id_dict[0])
#print(clust_id_dict[4])
Portfolio_Cluster.save_dend(link_mat, 0)


#pplot.savefig('dendrogram.png')
Portfolio_Cluster.save_dend_cut(link_mat, n_clust=n_clust)
#pplot.show()
