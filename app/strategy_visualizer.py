import numpy as np
from enum import Enum

import pandas as pd
from matplotlib import pyplot as plt


class Action(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


def print_operation(date, action: Action, open, money, shares):
    print(
        f'  DATE:{date.rjust(12)}    '
        f'ACTION: {action.value.lower().rjust(12)}    '
        f'  OPEN:{str(open)[:11].rjust(12)}    '
        f' MONEY:{str(money)[:11].rjust(12)}    '
        f'SHARES: {str(shares)[:11].rjust(12)}'
    )


def print_strategy(stock_data, ta_features, strategy, initial_money=100000):
    days = stock_data.shape[0]
    dates = stock_data['date'].to_numpy()
    open_prices = stock_data['open'].to_numpy()
    ta_features_numpy = ta_features.to_numpy()
    money = initial_money
    shares = 0
    buy_strategy, sell_strategy = np.array_split(strategy, 2)
    for i in range(1, days - 1):
        eval_buy = np.sum(ta_features_numpy[i - 1] * buy_strategy)
        eval_sell = np.sum(ta_features_numpy[i - 1] * sell_strategy)
        if money > 0 and eval_buy > 0 and eval_sell <= 0:
            shares = money / open_prices[i]
            money = 0
            print_operation(dates[i], Action.BUY, open_prices[i], money, shares)
        elif shares > 0 and eval_sell > 0 and eval_buy <= 0:
            money = shares * open_prices[i]
            shares = 0
            print_operation(dates[i], Action.SELL, open_prices[i], money, shares)
    if shares > 0:
        money = shares * open_prices[-1]
        shares = 0
        print_operation(dates[-1], Action.SELL, open_prices[-1], money, shares)
    print(
        f'\n{"-" * 115}\n'
        f'  INITIAL MONEY: {str(initial_money)[:11].rjust(12)}    '
        f'    FINAL MONEY: {str(money)[:11].rjust(12)}'
    )


def simulate_strategy(stock_data, ta_features, strategy, initial_money=100000):
    days = stock_data.shape[0]
    dates = stock_data['date'].to_numpy()
    open_prices = stock_data['open'].to_numpy()
    ta_features_numpy = ta_features.to_numpy()
    x_buy = []
    y_buy = []
    x_sell = []
    y_sell = []
    sum_money_and_money_in_shares = [initial_money]
    money = initial_money
    shares = 0
    buy_strategy, sell_strategy = np.array_split(strategy, 2)
    for i in range(1, days - 1):
        eval_buy = np.sum(ta_features_numpy[i - 1] * buy_strategy)
        eval_sell = np.sum(ta_features_numpy[i - 1] * sell_strategy)
        if money > 0 and eval_buy > 0 and eval_sell <= 0:
            shares = money / open_prices[i]
            money = 0
            x_buy.append(dates[i])
            y_buy.append(open_prices[i])
        elif shares > 0 and eval_sell > 0 and eval_buy <= 0:
            money = shares * open_prices[i]
            shares = 0
            x_sell.append(dates[i])
            y_sell.append(open_prices[i])
        sum_money_and_money_in_shares.append(money + shares * open_prices[i])
    if shares > 0:
        money = shares * open_prices[-1]
        x_sell.append(dates[-1])
        y_sell.append(open_prices[-1])
    sum_money_and_money_in_shares.append(money)
    return dates, open_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares


def simulate_best_possible_strategy(stock_data, initial_money=100000):
    days = stock_data.shape[0]
    dates = stock_data['date'].to_numpy()
    open_prices = stock_data['open'].to_numpy()
    x_buy = []
    y_buy = []
    x_sell = []
    y_sell = []
    sum_money_and_money_in_shares = [initial_money]
    money = initial_money
    shares = 0
    for i in range(1, days - 1):
        if open_prices[i] < open_prices[i + 1] and money > 0:
            shares = money / open_prices[i]
            money = 0
            x_buy.append(dates[i])
            y_buy.append(open_prices[i])
        elif open_prices[i] > open_prices[i + 1] and shares > 0:
            money = shares * open_prices[i]
            shares = 0
            x_sell.append(dates[i])
            y_sell.append(open_prices[i])
        sum_money_and_money_in_shares.append(money + shares * open_prices[i])
    if shares > 0:
        money = shares * open_prices[-1]
        x_sell.append(dates[-1])
        y_sell.append(open_prices[-1])
    sum_money_and_money_in_shares.append(money)
    return dates, open_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares


def plot_strategy(dates, open_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares):
    dates_cnt = len(dates)

    plt.style.use('bmh')
    plt.figure(figsize=(16, 18), dpi=400)
    plt.subplot(211)
    plt.plot(dates, open_prices, linewidth=0.75)
    plt.plot(x_buy, y_buy, 'g^', label=f'Buy')
    plt.plot(x_sell, y_sell, 'rv', label=f'Sell')
    plt.xlabel('Date')
    plt.ylabel('Open price')
    plt.title('Strategy visualization')
    plt.grid(True)
    plt.xticks(np.arange(0, dates_cnt - 1, dates_cnt // 20), rotation=45)
    plt.legend(loc='upper left')

    plt.subplot(212)
    plt.plot(dates, sum_money_and_money_in_shares, color='orange', linewidth=0.75)
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.title('Money + money in shares')
    plt.grid(True)
    plt.xticks(np.arange(0, dates_cnt - 1, dates_cnt // 20), rotation=45)

    plt.show()
