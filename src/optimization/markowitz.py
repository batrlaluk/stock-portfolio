import numpy as np
import math
import scipy.stats as stat
import cvxopt.solvers as solvers
from cvxopt import matrix
from src.clustering.Portfolio_Clustering import Portfolio_Cluster
from src.db.StockRegistry import StockRegistry
from matplotlib import pyplot as plt
from src.download.download_stock_data import get_close_values_of_the_stocks, draw_multiple_stock_data,get_market_performance



'''
#######################
# Optimization part:
#######################
'''

# Computes the annualized covariance matrix of the specified stock daily returns
def compute_covariance(daily_Returns):
    return np.cov(daily_Returns, rowvar=False) * 252


# Computes the annualized expected returns of the specified stock daily returns
def compute_expected_returns(daily_Returns):
    return np.power(stat.gmean(1+ daily_Returns, axis=0), 252) - 1

def compute_expected_returns_axis_1(daily_Returns):
    return np.power(stat.gmean(1+ daily_Returns, axis=1), 252) - 1

# Compute the daily returns of a matrix
def compute_daily_returns(daily_Prices):
    return np.divide(np.diff(daily_Prices, axis=0), daily_Prices[:-1, :] )

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


n_clust = 25
risk_free_rate = 0.027
cor_mat = Portfolio_Cluster.Correlation_Matrix(dailyReturnsMatrix)
dist_mat = Portfolio_Cluster.distance_Matrix(cor_mat)
link_mat = Portfolio_Cluster.complete_linkage(dist_mat)
cut_tree = Portfolio_Cluster.cut_tree(link_mat, n_clust)
clust_id_dict = Portfolio_Cluster.find_elements(cut_tree)
sharp_arr = Portfolio_Cluster.compute_sharp_ratios(dailyReturnsMatrix, risk_free_rate)
selected_stocks = Portfolio_Cluster.getTopStockFromAllClusters(clust_id_dict, sharp_arr)

ids = []

# The following code is to test the getTopStockFromStockList and getTopStockFromAllClusters methods
# print('top stock should be 3. The result is: ', getTopStockFromStockList([0,1,4], np.array([-1,3,5,12,1,0,8])))
# print('top stock by cluster should be [(2, 5), (3, 12)]. The result is: ', Portfolio_Cluster.getTopStockFromAllClusters({0: [0,1,2], 1: [3, 4]}, np.array([-1,3,5,12,1,0,8])))

# selected_stocks is a list of N stocks, each from one of N clusters, in a form (stock id, sharpe value)
#selected_stocks = Portfolio_Cluster.getTopStockFromAllClusters(clust_id_dict, sharp_arr)


id_list = []
for id in selected_stocks:
    id_list.append(id[0])

#ticker_correlation = np.zeros((n_clust,n_clust))
#for id, value in enumerate(id_list):
#    for id2, value2 in enumerate(id_list):
#        ticker_correlation[id][id2] = cor_mat[value][value2]
#
#print('Correlation mean for 25 stocks:', np.mean(ticker_correlation))
# ward correlation: 0.050722497829020441

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



plt.figure(1)
plt.plot(np.array(port_risk).reshape(len(rng),1), port_rets)
plt.plot(chosen_stock_risk, chosen_stock_ret, 'kx')

for i, ticker in enumerate(tickers):
    plt.annotate(ticker, xy=(chosen_stock_risk[i], chosen_stock_ret[i]), xytext=(chosen_stock_risk[i], chosen_stock_ret[i] + 0.01))
plt.xlabel('Risk')
plt.ylabel('Return')
plt.title('Efficient Frontier of found assets w/o shortselling and risk free asset')
plt.savefig('efficientfrontier_cut.png', dpi=400)


'''
#######################
# Simulation part:
#######################
'''

simulation_start_date = "2017-11-11"
simulation_end_date = "2018-11-10"

# weights for each portfolio calculation:

gmv_port = port_weights[:, np.argmin(port_risk)]
max_ret_port = port_weights[:, np.argmax(port_rets)]
eq_weight_port = np.array([1/n_clust] * n_clust).reshape((n_clust, 1))
max_SR_port = port_weights[:, np.argmax((np.array(port_rets) - risk_free_rate)/ np.array(port_risk).reshape((len(port_rets),)))]

# validation : it shoudl sum up all to 1.0
# max_SR_port.sum()

# download market data for simulation:
market_daily_close_values = get_market_performance(simulation_start_date, simulation_end_date )

# calculate daily returns
#market_daily_returns = np.diff(market_daily_close_values)
# normalizing daily returns data
normalized_market_returns = np.divide(np.diff(np.array(market_daily_close_values)),np.array(market_daily_close_values)[:-1])

#download efficient frontier portfolio daily returns for smulation:

portfolio_daily_close_values = get_close_values_of_the_stocks(tickers,simulation_start_date,simulation_end_date )

# draw seperate stock from efficient frontier
#draw_multiple_stock_data(tickers,simulation_start_date,simulation_end_date )

# Set the price to 0 where the stock DNO is not being traded anymore
for idx, row in enumerate(portfolio_daily_close_values['DNO'], start=0):
    if math.isnan(row):
        portfolio_daily_close_values['DNO'][idx] = 0

# Compute the daily returns
test_daily_ret = compute_daily_returns(np.array(portfolio_daily_close_values))

# Set the nan returns of DNO to 0
for idx, row in enumerate(test_daily_ret[:, 2]):
    if math.isnan(row):
        test_daily_ret[idx, 2] = 0

# Compute the daily return of each individual portfolio

SR_port_ret = np.zeros((len(test_daily_ret), 1))
EQW_port_ret = np.zeros((len(test_daily_ret), 1))
max_ret_port_ret = np.zeros((len(test_daily_ret), 1))
GMV_port_ret = np.zeros((len(test_daily_ret), 1))

for idx, day_ret in enumerate(test_daily_ret, start=0):
    SR_port_ret[idx] = day_ret.dot(max_SR_port)
    EQW_port_ret[idx] = day_ret.dot(eq_weight_port)
    max_ret_port_ret[idx] = day_ret.dot(max_ret_port)
    GMV_port_ret[idx] = day_ret.dot(gmv_port)

dates = portfolio_daily_close_values.index
plt.figure(2, figsize=(20, 9))
plt.ylabel('Returns')
plt.title('Cumulative sum of daily returns of each portfolio against the S&P 500 index')

plt.plot(dates[1:], np.cumsum(SR_port_ret), 'g', label='Max Sharpe rat. Port.')
plt.plot(dates[1:], np.cumsum(EQW_port_ret), 'k', label='Eq. weight. Port.')
plt.plot(dates[1:], np.cumsum(max_ret_port_ret), 'y', label='Max Ret. Port.')
plt.plot(dates[1:], np.cumsum(GMV_port_ret), 'm', label='Global minimum var. Port.')
plt.plot(dates[1:], np.cumsum(normalized_market_returns), 'b',label='S&P 500')
plt.legend()
#plt.plot(np.cumsum(np.diff(np.array(ddd), np.array(ddd)[:-1])))
plt.savefig('portfolio_simulation.png', dpi=400)



# Make a new plot with the portfolios plotted

SR_port_ret_plot = exp_ret.T.dot(max_SR_port)
GMV_port_ret_plot = exp_ret.T.dot(gmv_port)
EQW_port_ret_plot = exp_ret.T.dot(eq_weight_port)
max_ret_port_ret_plot = exp_ret.T.dot(max_ret_port)

SR_port_risk_plot = math.sqrt(max_SR_port.T.dot(cov_mat.dot(max_SR_port)))
GMV_port_risk_plot = math.sqrt(gmv_port.T.dot(cov_mat.dot(gmv_port)))
EQW_port_risk_plot = math.sqrt(eq_weight_port.T.dot(cov_mat.dot(eq_weight_port)))
max_ret_port_risk_plot = math.sqrt(max_ret_port.T.dot(cov_mat.dot(max_ret_port)))

used_portfolios_ret = [SR_port_ret_plot, GMV_port_ret_plot, EQW_port_ret_plot, max_ret_port_ret_plot]
used_portfolios_risk = [SR_port_risk_plot, GMV_port_risk_plot, EQW_port_risk_plot, max_ret_port_risk_plot]
port_names = ['Max SR', 'GMV','EQW','Max Ret']

plt.figure(3)
plt.plot(np.array(port_risk).reshape(len(rng),1), port_rets)
plt.plot(chosen_stock_risk, chosen_stock_ret, 'kx')
plt.plot(used_portfolios_risk, used_portfolios_ret, 'bx')
for i, ticker in enumerate(tickers):
    plt.annotate(ticker, xy=(chosen_stock_risk[i], chosen_stock_ret[i]), xytext=(chosen_stock_risk[i], chosen_stock_ret[i] + 0.01))
    if i < len(port_names) -2:
        plt.annotate(port_names[i], xy=(used_portfolios_risk[i], used_portfolios_ret[i]),
                    xytext=(used_portfolios_risk[i], np.array(used_portfolios_ret[i]) + 0.01))

plt.xlabel('Risk')
plt.ylabel('Return')
plt.title('Efficient Frontier of found assets w/o shortselling and risk free asset')
plt.savefig('efficientfrontier_portfolios_plotted.png', dpi=400)

