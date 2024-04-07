import random
import pandas as pd
import numpy as np

from deap import creator, base, tools


def setup_toolbox(stock_data: pd.DataFrame, ta_features: pd.DataFrame) -> base.Toolbox:
    ta_features_n = len(ta_features.columns)

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("attr_uniform", random.uniform, -1, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_uniform, n=ta_features_n)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual, _stock_data, _ta_features):
        money = 1000
        shares = 0
        for i in range(len(_ta_features) - 1):
            _eval = np.sum(_ta_features.iloc[i].to_numpy() * np.array(individual))
            if _eval > 0 and money > 0:
                shares = money / _stock_data.iloc[i]['close']
                money = 0
            elif _eval < 0 and shares > 0:
                money = shares * _stock_data.iloc[i]['close']
                shares = 0
        if shares > 0:
            money = shares * _stock_data.iloc[-1]['close']

        return money,

    toolbox.register("evaluate", evaluate, _stock_data=stock_data, _ta_features=ta_features)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=10, low=-1, up=1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    return toolbox


def setup_stats() -> tools.Statistics:
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    return stats


