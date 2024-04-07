import numpy as np
from enum import Enum
from matplotlib import pyplot as plt


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
    dates = stock_data['date'].to_numpy()
    close_prices = stock_data['close'].to_numpy()
    money = initial_money
    shares = 0
    for i in range(len(ta_features) - 1):
        if np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) > 0 and money > 0:
            shares = money / close_prices[i]
            money = 0
            print_operation(dates[i], Action.BUY, close_prices[i], money, shares)
        elif np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) < 0 and shares > 0:
            money = shares * close_prices[i]
            shares = 0
            print_operation(dates[i], Action.SELL, close_prices[i], money, shares)
    if shares > 0:
        money = shares * close_prices[-1]
        shares = 0
        print_operation(dates[-1], Action.SELL, close_prices[-1], money, shares)
    print(
        f'\n{"-" * 115}\n'
        f'  INITIAL MONEY: {str(initial_money)[:11].rjust(12)}    '
        f'    FINAL MONEY: {str(money)[:11].rjust(12)}'
    )


def simulate_strategy(stock_data, ta_features, strategy, initial_money=1000):
    dates = stock_data['date'].to_numpy()
    close_prices = stock_data['close'].to_numpy()
    x_buy = []
    y_buy = []
    x_sell = []
    y_sell = []
    sum_money_and_money_in_shares = []
    money = initial_money
    shares = 0
    for i in range(len(ta_features) - 1):
        if np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) > 0 and money > 0:
            shares = money / close_prices[i]
            money = 0
            x_buy.append(dates[i])
            y_buy.append(close_prices[i])
        elif np.sum(ta_features.iloc[i].to_numpy() * np.array(strategy)) < 0 and shares > 0:
            money = shares * close_prices[i]
            shares = 0
            x_sell.append(dates[i])
            y_sell.append(close_prices[i])
        sum_money_and_money_in_shares.append(money + shares * close_prices[i])
    if shares > 0:
        money = shares * close_prices[-1]
        x_sell.append(dates[-1])
        y_sell.append(close_prices[-1])
    sum_money_and_money_in_shares.append(money)
    return dates, close_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares


def simulate_best_possible_strategy(stock_data, initial_money=1000):
    dates = stock_data['date'].to_numpy()
    close_prices = stock_data['close'].to_numpy()
    x_buy = []
    y_buy = []
    x_sell = []
    y_sell = []
    sum_money_and_money_in_shares = []
    money = initial_money
    shares = 0
    for i in range(len(dates) - 1):
        if stock_data.iloc[i]['close'] < stock_data.iloc[i + 1]['close'] and money > 0:
            shares = money / close_prices[i]
            money = 0
            x_buy.append(dates[i])
            y_buy.append(close_prices[i])
        elif stock_data.iloc[i]['close'] > stock_data.iloc[i + 1]['close'] and shares > 0:
            money = shares * close_prices[i]
            shares = 0
            x_sell.append(dates[i])
            y_sell.append(close_prices[i])
        sum_money_and_money_in_shares.append(money + shares * close_prices[i])
    if shares > 0:
        money = shares * close_prices[-1]
        x_sell.append(dates[-1])
        y_sell.append(close_prices[-1])
    sum_money_and_money_in_shares.append(money)
    return dates, close_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares


def plot_strategy(dates, close_prices, x_buy, y_buy, x_sell, y_sell, sum_money_and_money_in_shares):
    dates_cnt = len(dates)

    plt.style.use('bmh')
    plt.figure(figsize=(16, 18), dpi=400)
    plt.subplot(211)
    plt.plot(dates, close_prices, linewidth=0.75)
    plt.plot(x_buy, y_buy, 'g^', label=f'Buy')
    plt.plot(x_sell, y_sell, 'rv', label=f'Sell')
    plt.xlabel('Date')
    plt.ylabel('Close price')
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
