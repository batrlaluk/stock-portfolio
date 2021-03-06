# use consoelt to download library: pip install fix_yahoo_finance --upgrade --no-cache-dir

import matplotlib.pyplot as plt
import fix_yahoo_finance as yf  
import pylab as pylab
from matplotlib.font_manager import FontProperties

default_start_date = '2017-10-12'
default_end_date = '2018-10-11'
default_stock_name = 'AAPL'
default_stocks_name = ['AAPL','AA']

def test_download_process():
    
    data = yf.download(default_stock_name,default_start_date,default_end_date)
    data.Close.plot()
    plt.show()


def draw_stock_data(stock_name,start_date,end_date):
    
    data = yf.download(stock_name,start_date,end_date)
    data.Close.plot()
    plt.show()

def draw_multiple_stock_data(stock_names,start_date,end_date):
    
    data = yf.download(stock_names,start_date,end_date)
    data.Close.plot(figsize=(20, 12))
    plt.legend(bbox_to_anchor=(1.04, 1), ncol=1, loc="upper left", borderaxespad=0.)
    plt.savefig("portfolio_simulation.png", dpi=400)
    plt.show()
    
    
def get_single_stock_data(stock_name,start_date,end_date):
    
    data = yf.download(stock_name,start_date,end_date)
    return data


def get_multiple_stock_data(stock_names,start_date,end_date):
    
    data = yf.download(stock_names,start_date,end_date)
    return data


def get_close_values_of_the_stocks(stock_names,start_date,end_date):
    
    data = yf.download(stock_names,start_date,end_date)
    return data['Close']

def get_adjusted_close_values_of_the_stocks(stock_names,start_date,end_date):
    
    data = yf.download(stock_names,start_date,end_date)
    return data['Adj Close']

def get_market_performance(start_date, end_date):
    
    data = data = yf.download('^GSPC', start_date, end_date )
    return data['Close']
    