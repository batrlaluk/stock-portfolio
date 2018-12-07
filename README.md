# stock-portfolio
School project for Computational Tools for Data Science course at DTU. 


**Goal:** To create an optimized stock portfolio based on historical daily prices of the New York Stock Exchange and NASDAQ with the help of hierarchical clustering.

**How to run:**

1. Download the dataset (https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs/home) into `stock-portfolio/src/data` so that the `data` folder looks like this: `data/Stocks` and `data/ETFs`.
2. Go to `src/db/` and run `import_data.py` script. That will create new database based on the files downloaded in the previous step.
3. Go to `src/optimization` and run `markowitz.py` to get the portfolio results.

**Colaborators:**
- [Ali Saleem](https://github.com/alisaleem96)
- [Kamil Kacperski](https://github.com/kakacper1)
- [Lukáš Bátrla](https://github.com/batrlaluk)
