import random
import pandas as pd
import numpy as np
import multiprocessing

from math import log2
from deap import creator, base, tools, cma


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


def eaGenerateUpdateRestarts(toolbox, nrestarts, maxngens, halloffame, stats, verbose=__debug__):
    logbooks = []
    best_logbook = None
    best_fitness = 0

    for i in range(nrestarts):
        strategy = toolbox.generate_strategy()
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        logbook = tools.Logbook()
        logbooks.append(logbook)
        logbook.header = ['restart', 'gen', 'nevals', 'sigma'] + stats.fields

        stds = []

        for gen in range(maxngens):
            # Generate a new population
            population = toolbox.generate()
            # Evaluate the individuals
            fitnesses = toolbox.map(toolbox.evaluate, population)
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit

            halloffame.update(population)

            # Update the strategy with the evaluated individuals
            toolbox.update(population)

            record = stats.compile(population)
            logbook.record(gen=gen, nevals=len(population), restart=i, sigma=strategy.sigma, **record)
            if verbose:
                print(logbook.stream)

            stds.append(np.std(fitnesses))
            if len(stds) > 20 and np.mean(stds[-20:]) < 1e-1:
                break

        if halloffame[0].fitness.values[0] > best_fitness:
            best_fitness = halloffame[0].fitness.values[0]
            best_logbook = logbook

    return best_logbook, logbooks


def mutUniform(individual, low, up, indpb):
    size = len(individual)

    for i in range(size):
        if random.random() < indpb:
            individual[i] = random.random() * (up - low) + low

    return individual,


def evaluate(
        individual: np.ndarray,
        days: int,
        ta_features: np.ndarray,
        stock_data: np.ndarray,
        initial_money: int,
        commission: float
):
    money = initial_money
    shares = 0
    individual_buy, individual_sell = np.array_split(individual, 2)
    for i in range(1, days - 1):
        eval_buy = np.sum(ta_features[i - 1] * individual_buy)
        eval_sell = np.sum(ta_features[i - 1] * individual_sell)
        if money > 0 and eval_buy > 0:
            shares = (money * (1 - commission)) / stock_data[i, 1]
            money = 0
        elif shares > 0 and eval_sell > 0:
            money = shares * stock_data[i, 1] * (1 - commission)
            shares = 0
    if shares > 0:
        money = shares * stock_data[-1, 1] * (1 - commission)

    return money,


def setup_toolbox(
        stock_data: pd.DataFrame,
        ta_features: pd.DataFrame,
        initial_money: int,
        commission: float
) -> base.Toolbox:
    N = len(ta_features.columns) * 2

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("attr_uniform", random.uniform, -1, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_uniform, n=N)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    days = ta_features.shape[0]
    ta_features = ta_features.to_numpy()
    stock_data = stock_data.to_numpy()
    # stock_data.to_numpy() columns:
    # 0 - date, 1 - open, 2 - high, 3 - low, 4 - close, 5 - volume

    toolbox.register(
        "evaluate",
        evaluate,
        days=days,
        ta_features=ta_features,
        stock_data=stock_data,
        initial_money=initial_money,
        commission=commission
    )

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

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


def setup_ea(
        stock_data: pd.DataFrame,
        ta_features: pd.DataFrame,
        pop_size: int,
        tournament_size_pop_ratio: float,
        initial_money: int,
        commission: float
):
    toolbox = setup_toolbox(stock_data, ta_features, initial_money, commission)

    toolbox.register("mate", cxTwoPointTwoVectorsNumpy)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=10, low=-1, up=1, indpb=0.05)
    # toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.5, indpb=0.1)
    # toolbox.register("mutate", mutUniform, low=-1, up=1, indpb=0.1)
    tournament_size = 2 ** int(log2(pop_size * tournament_size_pop_ratio))
    toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    population = toolbox.population(n=pop_size)
    stats = setup_stats()
    hall_of_fame = tools.HallOfFame(1, compare_individuals)

    return population, toolbox, stats, hall_of_fame


def setup_cmaes(
        stock_data: pd.DataFrame,
        ta_features: pd.DataFrame,
        lambda_: int,
        initial_money: int,
        commission: float
):
    N = len(ta_features.columns) * 2

    toolbox = setup_toolbox(stock_data, ta_features, initial_money, commission)
    stats = setup_stats()
    hall_of_fame = tools.HallOfFame(1, compare_individuals)

    toolbox.register("generate_strategy", cma.Strategy, centroid=np.random.uniform(-5, 5, N), sigma=1, lambda_=lambda_)

    return toolbox, stats, hall_of_fame
