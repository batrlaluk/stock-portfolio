import numpy as np
import scipy.stats as sci
import scipy.spatial as spat_sci
import scipy.cluster.hierarchy as clust_sci
from matplotlib import pyplot as pplot

class Portfolio_Cluster:

    # This method computes the spearman correlation coefficient matrix
    def Correlation_Matrix(Returns):
        spearman_coeff, p_val = sci.spearmanr(Returns)
        return spearman_coeff

    # This method computes the distance matrix with metric 1-abs(C) where C denotes correlation
    # Returns a condensed matrix
    def distance_Matrix(Corr_Mat):
        n, m = np.shape(Corr_Mat)
        dist_mat = np.empty((n, n))
        for i in range(0,n):
            for j in range(0,m):
                dist_mat[i, j] = 1-abs(Corr_Mat[i, j])

        np.fill_diagonal(dist_mat, 0)                   # If not done, the diagonal will contain values very close to 0 instead
        return spat_sci.distance.squareform(dist_mat)

    # This method computes the "complete" linkage between the specified condensed distance matrix
    # Returns the hierarchical clustering encoded as a linkage matrix (From documentation)
    def link(Dist_Mat):
        return clust_sci.linkage(dist_mat, method='complete')

    # This method plots the dendogram of a linkage matrix. Specify n_clust to cut tree to obtain n_clust amount of
    # clusters on your dendogram plot. Set n_clust = 0 if you wish to see the whole dendogram
    def plot_dend(link_Mat, n_clust):
        pplot.figure()
        dendo = clust_sci.dendrogram(link_mat, p=n_clust, truncate_mode='lastp')
        pplot.draw()

    # Cuts a dendogram tree and return a list of
    def cut_tree(link_Mat, clust_numb):
        return clust_sci.cut_tree(link_mat, n_clusters= clust_numb)

    # This method outputs what elements belong to what cluster in the n-amount of clusters you have chosen when you cut
    # the dendogram tree. Requires a cut_tree object which is obtained from the scipy.clusters.hierarchy.cut_tree
    def find_elements(tree_cut):
        clust_id_dict = {}
        idx = 0
        for clust_id in cut_tree:
            if clust_id[0] not in clust_id_dict.keys():
                clust_id_dict[clust_id[0]] = [idx]
            else:
                clust_id_dict[clust_id[0]].append(idx)
            idx += 1
        return clust_id_dict

Ret = np.random.rand(100,20)*10
n_clust = 5

cor_mat = Portfolio_Cluster.Correlation_Matrix(Ret)
dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)
link_mat = Portfolio_Cluster.link(dist_mat)
cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)






#print(cor_mat)
#print("\n")
#print(dist_mat)
#print("\n")
#print(link_mat)
#print("\n")
print(cut_tree)
#print("\n")
print(clust_id_dict.keys())
print(clust_id_dict.values())
print(clust_id_dict[0])
print(clust_id_dict[4])
Portfolio_Cluster.plot_dend(link_mat, 0)
Portfolio_Cluster.plot_dend(link_mat, n_clust=n_clust)
pplot.show()