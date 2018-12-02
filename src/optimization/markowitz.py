import numpy as np
import scipy.stats as stat
#import sys
#sys.path.append('C:/Program Files/Python37/Library/bin')
import cvxopt.solvers as solvers
from cvxopt import matrix
from src.clustering.Portfolio_Clustering import Portfolio_Cluster
from src.db.StockRegistry import StockRegistry



# Computes the annualized covariance matrix of the specified stock daily returns
def compute_covariance(daily_Returns):
    return np.cov(daily_Returns) * 252


# Computes the annualized expected returns of the specified stock daily returns
def compute_expected_returns(daily_Returns):
    return np.power(stat.gmean(1+ daily_Returns, axis=0), 252) - 1


def compute_efficientFrontier(Cov_Mat, expected_Returns, specified_Return):
    n, m = np.shape(Cov_Mat)
    Hess = Cov_Mat
    Lin = np.zeros((n, 1))
    Eq = np.ones((2, m))
    Eq[0, :] = expected_Returns
    Eq_rhs = np.ones((2, 1))
    Eq_rhs[0] = specified_Return
    Ineq = np.diag([-1.0] * n)
    Ineq_rhs = np.zeros((n, 1))
    solver_info = solvers.qp(P=matrix(Hess), q=matrix(Lin), A=matrix(Eq), b=matrix(Eq_rhs), G=matrix(Ineq), h=matrix(Ineq_rhs))

    Port_Risk = np.sqrt(np.array(solver_info['x']).T.dot(np.array(Cov_Mat)).dot(np.array(solver_info['x'])))
    port_Info = np.array(solver_info['x'])
    return np.vstack((port_Info, specified_Return, Port_Risk, np.sum(port_Info)))


start_date = "2011-01-03"
end_date = "2017-11-10"

# 2. pcik name of dictionary !
registry = StockRegistry("C:/Users/Ejer/Dropbox/UNI/7. Semester/Computational Tools for Data Science/stock-portfolio/src/db/stock_database.sqlite")

valid_ids = registry.getValidStockIds(start_date, end_date)

validStockDict = dict()
for idx, stock_id in enumerate(valid_ids):
    validStockDict[idx] = stock_id
dailyReturnsMatrix = registry.gethDailyReturnsForRequestedStockIds(validStockDict, start_date, end_date)


cov_mat = compute_covariance(dailyReturnsMatrix)
exp_ret = compute_expected_returns(dailyReturnsMatrix)
info = compute_efficientFrontier(cov_mat[:5,:5], exp_ret[:5], 0.22)
print(info)
#print("Shape of returns matrix", dailyReturnsMatrix.shape)

#print('Daily Returns:', compute_expected_returns(dailyReturnsMatrix))
#n_clust = 10
#cor_mat = Portfolio_Cluster.Correlation_Matrix(dailyReturnsMatrix)
#dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)
#link_mat = Portfolio_Cluster.ward_linkage(dist_mat)
#cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)
#registry.close()