import numpy as np
import scipy.stats as stat
import cvxopt.solvers as solvers
from cvxopt import matrix
from src.clustering.Portfolio_Clustering import Portfolio_Cluster
from src.db.StockRegistry import StockRegistry
from matplotlib import pyplot as plt

# Computes the annualized covariance matrix of the specified stock daily returns
def compute_covariance(daily_Returns):
    return np.cov(daily_Returns, rowvar=False) * 252


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
    port_dict = {}
    port_dict['w'] = port_Info
    port_dict['risk'] = Port_Risk
    port_dict['ret'] = specified_Return
    return port_dict


start_date = "2011-01-03"
end_date = "2017-11-10"

# 2. pcik name of dictionary !
registry = StockRegistry("C:/Users/Ejer/Dropbox/UNI/7. Semester/Computational Tools for Data Science/stock-portfolio/src/db/stock_database.sqlite")

valid_ids = registry.getValidStockIds(start_date, end_date)

validStockDict = dict()
for idx, stock_id in enumerate(valid_ids):
    validStockDict[idx] = stock_id
dailyReturnsMatrix = registry.gethDailyReturnsForRequestedStockIds(validStockDict, start_date, end_date)


n_clust = 15
risk_free_rate = 0.027
cor_mat = Portfolio_Cluster.Correlation_Matrix(dailyReturnsMatrix)
dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)
link_mat = Portfolio_Cluster.ward_linkage(dist_mat)
cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)
clust_id_dict = Portfolio_Cluster.find_elements(cut_tree)
sharp_arr = Portfolio_Cluster.compute_sharp_ratios(dailyReturnsMatrix, risk_free_rate)
selected_stocks = Portfolio_Cluster.getTopStockFromAllClusters(clust_id_dict, sharp_arr)

# The following code is to test the getTopStockFromStockList and getTopStockFromAllClusters methods
# print('top stock should be 3. The result is: ', getTopStockFromStockList([0,1,4], np.array([-1,3,5,12,1,0,8])))
# print('top stock by cluster should be [(2, 5), (3, 12)]. The result is: ', Portfolio_Cluster.getTopStockFromAllClusters({0: [0,1,2], 1: [3, 4]}, np.array([-1,3,5,12,1,0,8])))

# selected_stocks is a list of N stocks, each from one of N clusters, in a form (stock id, sharpe value)
selected_stocks = Portfolio_Cluster.getTopStockFromAllClusters(clust_id_dict, sharp_arr)


id_list = []
for id in selected_stocks:
    id_list.append(id[0])

tickers = [registry.getStockById(validStockDict[i])[0][1] for i in id_list]


exp_ret = compute_expected_returns(dailyReturnsMatrix[:, id_list])
cov_mat = compute_covariance(dailyReturnsMatrix[:, id_list])

max_ret = max(exp_ret)
min_ret = min(exp_ret)

current_val = min_ret
rng = []
step = 0.001
while current_val <= max_ret:
    rng.append(current_val)
    current_val += step

port_rets = []
port_risk = []
port_weights = np.zeros((n_clust, len(rng)))
count = 0
for spec_ret in rng:
    port_dict = compute_efficientFrontier(cov_mat, exp_ret, spec_ret)
    port_rets.append(port_dict['ret'])
    port_risk.append(port_dict['risk'])
    port_weights[:, count] = np.array(port_dict['w']).flatten()
    count += 1


chosen_stock_ret = exp_ret
chosen_stock_risk = np.sqrt(cov_mat.diagonal())



plt.figure()
plt.plot(np.array(port_risk).reshape(len(rng),1), port_rets)
plt.plot(chosen_stock_risk, chosen_stock_ret, 'kx')

for i, ticker in enumerate(tickers):
    plt.annotate(ticker, xy=(chosen_stock_risk[i], chosen_stock_ret[i]), xytext=(chosen_stock_risk[i], chosen_stock_ret[i] + 0.01))
plt.xlabel('Risk')
plt.ylabel('Return')
plt.title('Efficient Frontier of found assets w/o shortselling and risk free asset')
plt.savefig('efficientfrontier_cut.png', dpi=400)


