# This script runs the experiment.
# Author: Brendan Saliba
# Company: Farpoint AI, LLC
# https://farpointai.com

# IMPORTS
# ------------------------------------------------------------------------------------------------------------

import pickle
import math
import matplotlib.pyplot as plt
import warnings

from functions_and_classes import Account, predict


# PREPARE FOR EXPERIMENT
# ------------------------------------------------------------------------------------------------------------

# get the main df of stock history
with open("main.pickle", "rb") as a:
    main = pickle.load(a)
a.close()

# get list of tickers
with open("sp500tickers.pickle", "rb") as b:
    tickers = pickle.load(b)
b.close()

# create account
myacc = Account()
warnings.filterwarnings('ignore')



# RUN EXPERIMENT
# ------------------------------------------------------------------------------------------------------------

ticker = "AAL"  # ticker we want to trade
win_size = 14  # size of the window for feature generation (keep this at 14)
length = len(main)
starting_point = 4500  # index to start at in the main df for testing (could be 14 to 5000)
acc_value_hist = []

for i in range(starting_point, length):

    subdf = main[i - win_size:i].copy()  # create subdf of main df
    share_price = subdf[ticker].iloc[-1]
    date = subdf[ticker].index[-1]

    if not math.isnan(share_price):

        prediction = predict(ticker, subdf)[0]

        print(i, prediction, share_price)
        if prediction == 1:
            myacc.buy_stock(ticker, share_price, date)  # BUY
        elif prediction == -1:
            myacc.sell_stock(ticker, share_price, date)  # SELL
        else:
            print("Hold")

        acc_value_hist.append(myacc.get_acc_value(share_price))

    if i == length-1:  # sell positions on the last iteration
        myacc.sell_stock(ticker, share_price, date)


## SHOW RESULTS

# final account value
print(myacc.check_account())

# write trade history into a text file
hist = myacc.history

# # Uncomment if you want the history
# with open('AAL_hist.txt', 'w') as f:
#     for item in hist:
#         f.write("%s\n" % item)
# f.close()

# plot stock over the period traded and account value
fig, (a1, a2) = plt.subplots(2, 1)
a1.plot(main[ticker][starting_point:])
a1.set_title("Stock Price")
a1.ylabel("Dollars")

a2.plot(acc_value_hist, 'tab:green')
a2.set_title("Account Value")
a2.xlabel("Days Elapsed")
a2.ylabel("Dollars")

plt.show()
