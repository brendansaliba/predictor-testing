# This script contains the account class and functions necessary for the experiment.
# Author: Brendan Saliba
# Company: Farpoint AI, LLC
# https://farpointai.com

# IMPORTS
# ------------------------------------------------------------------------------------------------------------

import pickle
import pandas as pd
import datetime as dt
import time
import yfinance as yf
import numpy as np
import math

from pandas_datareader import data as pdr

yf.pdr_override()  # fix broke stuff


# CLASSES
# ------------------------------------------------------------------------------------------------------------

class Account:
    balance = 0
    positions = {}
    history = []

    def __init__(self):
        self.balance = 10000
        self.positions = {}
        self.history = []
        print("Acc init.. balance {}".format(self.balance))

    def get_acc_value(self, share_price):
        total = 0
        for ticker in self.positions:
            position_value = self.positions[ticker]['shares'] * share_price
            total += position_value
        total += self.balance
        return total

    def check_account(self):
        print("Cash balance: {}".format(self.balance))
        if self.positions:
            print("Positions: ", "\n", self.positions, "\n")

    def get_history(self):
        print("History: ", "\n", self.history)

    def buy_stock(self, ticker, share_price, date):
        if ticker not in self.positions:
            try:
                num_shares = math.floor(self.balance / share_price)
                if num_shares * share_price > 1000000:
                    num_shares = math.floor(1000000 / share_price)
            except:
                print("It broke again")
                self.check_account()
                print("The share price is {}".format(share_price))

            action = "Bought {} at {} ({} shares on {})".format(ticker, share_price, num_shares, date)

            self.balance = self.balance - (share_price * num_shares)
            self.history.append(action)
            self.positions[ticker] = {'shares': num_shares, 'purchase price': share_price}
            print(action)
        else:
            print("Already have shares of {}".format(ticker))

    def sell_stock(self, ticker, share_price, date):
        # check to see if you hold the stock, if so, continue
        if ticker in self.positions:
            # if you do hold the stock, calculate your profit/loss then sell it
            price_change = share_price - self.positions[ticker]['purchase price']
            position_net_change = price_change * self.positions[ticker]['shares']
            action = "Sold {} at {} ({} shares on {})".format(ticker, share_price, self.positions[ticker]['shares'],
                                                              date)
            print(action)
            self.balance = self.balance + (share_price * self.positions[ticker]['shares'])
            self.history.append(action)
            self.positions.pop(ticker)
        else:
            print('You do not hold any shares of {}'.format(ticker))


# FUNCTIONS
# ------------------------------------------------------------------------------------------------------------

# gets historical stock data for the S&P 500
def get_data_from_yahoo_and_compile_into_one_df():

    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    f.close()

    # create a main df for the data that will be used to make the features
    main_df = pd.DataFrame()

    # set the start and end dates for the yfinance calls
    start = '2000-01-01'
    end = dt.datetime.now()

    for count, ticker in enumerate(tickers):

        # make a temp df filled with the price data for the ticker and do a bunch of shit to it
        fuckyahoofinance = True
        while fuckyahoofinance:
            try:
                ticker_df = pdr.get_data_yahoo(ticker, start, end)
                fuckyahoofinance = False
            except:
                print("Waiting 3 seconds you fucking bitch")
                time.sleep(3)

        ticker_df.reset_index(inplace=True)
        ticker_df.set_index("Date", inplace=True)
        ticker_df.rename(columns={'Close': ticker}, inplace=True)
        ticker_df.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume'], 1, inplace=True)

        # start to fill up the main df with the data needed
        if main_df.empty:
            main_df = ticker_df
        else:
            main_df = main_df.join(ticker_df, how='outer')

        # counter to see where we are
        if count % 10 == 0:
            print(count)

        main_df = main_df[~main_df.index.duplicated(keep='first')]

    return main_df

# extracts feature from data and makes a prediction
def predict(ticker, df):
    # get the classifier for the ticker in question
    with open("classifiers/{}.pickle".format(ticker), "rb") as c:
        clf = pickle.load(c)
    c.close()

    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    f.close()

    hm_days = 7

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change(hm_days)  # changed the period from default (1) to hm_days
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    X = df_vals.values

    reshaped_feature = X[-1][0:505].reshape(1, -1)
    prediction = clf.predict(reshaped_feature)

    return prediction


## UNCOMMENT AND RUN THIS CODE IF
# main = get_data_from_yahoo_and_compile_into_one_df()
#
# with open("main.pickle", "wb") as f:
#     pickle.dump(main, f)
# f.close()
