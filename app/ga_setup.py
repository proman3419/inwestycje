import random
import pandas as pd
import numpy as np

from math import log2
from deap import creator, base, tools


def cxTwoPointTwoVectorsNumpy(ind1: np.ndarray, ind2: np.ndarray):
    """
    Execute a two points crossover for an individual that is composed of two vectors of equal length.
    The crossover is applied in the first vector and then in the second vector.
    Also, the crossover is executed with copy on the input individuals. The copy is required because the slicing
    in numpy returns a view of the data, which leads to a self overwriting in the swap operation.
    """
    size = len(ind1) // 2
    for i in range(2):
        offset = size * i
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size - 1)
        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else:  # Swap the two cx points
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        cxpoint1 += offset
        cxpoint2 += offset
        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
            = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

    return ind1, ind2


def evaluate(individual: np.ndarray, days: int, ta_features: np.ndarray, stock_data: np.ndarray):
    money = 1000
    shares = 0
    individual_buy, individual_sell = np.array_split(individual, 2)
    for i in range(days - 1):
        eval_buy = np.sum(ta_features[i] * individual_buy)
        eval_sell = np.sum(ta_features[i] * individual_sell)
        if money > 0 and eval_buy > 0 and eval_sell <= 0:
            shares = money / stock_data[i, 4]
            money = 0
        elif shares > 0 and eval_sell > 0 and eval_buy <= 0:
            money = shares * stock_data[i, 4]
            shares = 0
    if shares > 0:
        money = shares * stock_data[-1, 4]

    return money,


def setup_toolbox(stock_data: pd.DataFrame, ta_features: pd.DataFrame, pop_size: int) -> base.Toolbox:
    ta_features_n = len(ta_features.columns)
    individual_n = ta_features_n * 2

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("attr_uniform", random.uniform, -1, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_uniform, n=individual_n)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    days = ta_features.shape[0]
    ta_features_numpy = ta_features.to_numpy()
    stock_data_numpy = stock_data.to_numpy()
    # stock_data_numpy columns:
    # 0 - date, 1 - open, 2 - high, 3 - low, 4 - close, 5 - volume

    toolbox.register("evaluate", evaluate, days=days, ta_features=ta_features_numpy, stock_data=stock_data_numpy)
    toolbox.register("mate", cxTwoPointTwoVectorsNumpy)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=10, low=-1, up=1, indpb=0.05)

    tournament_size = 2 ** int(log2(pop_size * 0.2))
    toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    return toolbox


def setup_stats() -> tools.Statistics:
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    return stats


def compare_individuals(ind1: np.ndarray, ind2: np.ndarray) -> bool:
    return (ind1 == ind2).all()


def setup_ga(stock_data: pd.DataFrame, ta_features: pd.DataFrame, pop_size: int):
    toolbox = setup_toolbox(stock_data, ta_features, pop_size)
    population = toolbox.population(n=pop_size)
    stats = setup_stats()
    hall_of_fame = tools.HallOfFame(1, compare_individuals)

    return population, toolbox, stats, hall_of_fame
