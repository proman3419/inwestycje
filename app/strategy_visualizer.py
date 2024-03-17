import numpy as np
from enum import Enum

import pandas as pd
from matplotlib import pyplot as plt

from preprocessing import preprocess_data


class Action(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


def print_operation(date, action: Action, close, money, shares):
    print(
        f'  DATE:{date.rjust(12)}    '
        f'ACTION: {action.value.lower().rjust(12)}    '
        f' CLOSE:{str(close)[:11].rjust(12)}    '
        f' MONEY:{str(money)[:11].rjust(12)}    '
        f'SHARES: {str(shares)[:11].rjust(12)}'
    )


def print_strategy(stock_data, ta_features, strategy, initial_money=1000):
    money = initial_money
    shares = 0
    for i in range(len(ta_features) - 1):
        if np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) > 0 and money > 0:
            shares = money / stock_data.iloc[i]['close']
            money = 0
            print_operation(stock_data.iloc[i]['date'], Action.BUY, stock_data.iloc[i]['close'], money, shares)
        elif np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) < 0 and shares > 0:
            money = shares * stock_data.iloc[i]['close']
            shares = 0
            print_operation(stock_data.iloc[i]['date'], Action.SELL, stock_data.iloc[i]['close'], money, shares)
    if shares > 0:
        money = shares * stock_data.iloc[-1]['close']
        shares = 0
        print_operation(stock_data.iloc[-1]['date'], Action.SELL, stock_data.iloc[-1]['close'], money, shares)
    print(
        f'\n{"-" * 115}\n'
        f'  INITIAL MONEY: {str(initial_money)[:11].rjust(12)}    '
        f'    FINAL MONEY: {str(money)[:11].rjust(12)}'
    )


def plot_strategy(stock_data, ta_features, strategy, initial_money=1000):
    x = stock_data['date'].to_numpy()
    x_buy = []
    y_buy = []
    x_sell = []
    y_sell = []
    y_close = stock_data['close'].to_numpy()
    y_sum_money_and_money_in_shares = []
    money = initial_money
    shares = 0
    for i in range(len(ta_features) - 1):
        if np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) > 0 and money > 0:
            shares = money / stock_data.iloc[i]['close']
            money = 0
            x_buy.append(stock_data.iloc[i]['date'])
            y_buy.append(stock_data.iloc[i]['close'])
        elif np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) < 0 and shares > 0:
            money = shares * stock_data.iloc[i]['close']
            shares = 0
            x_sell.append(stock_data.iloc[i]['date'])
            y_sell.append(stock_data.iloc[i]['close'])
        y_sum_money_and_money_in_shares.append(money + shares * stock_data.iloc[i]['close'])
    if shares > 0:
        money = shares * stock_data.iloc[-1]['close']
        y_sum_money_and_money_in_shares.append(money)
        x_sell.append(stock_data.iloc[-1]['date'])
        y_sell.append(stock_data.iloc[-1]['close'])

    plt.style.use('bmh')
    plt.figure(figsize=(16, 18), dpi=400)
    plt.subplot(211)
    plt.plot(x, y_close, linewidth=0.75)
    plt.plot(x_buy, y_buy, 'g^', label=f'Buy')
    plt.plot(x_sell, y_sell, 'rv', label=f'Sell')
    plt.xlabel('Date')
    plt.ylabel('Close price')
    plt.title('Strategy visualization')
    plt.grid(True)
    plt.xticks(np.arange(0, len(x) - 1, len(x) // 20), rotation=45)
    plt.legend(loc='upper left')

    plt.subplot(212)
    plt.plot(x, y_sum_money_and_money_in_shares, color='orange', linewidth=0.75)
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.title('Money + money in shares')
    plt.grid(True)
    plt.xticks(np.arange(0, len(x) - 1, len(x) // 20), rotation=45)

    plt.show()
