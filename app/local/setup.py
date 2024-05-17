import random
import pandas as pd
import numpy as np
import multiprocessing

from math import log2
from deap import creator, base, tools, cma
from time import time

from deap.algorithms import varAnd

from storage_utils import init_dump_dir, save_strategy, save_logbook, add_summary


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


def dump_results(dirname_base, toolbox, halloffame, logbook, generations, start_time, save_simulation_params):
    strategy = halloffame[0]
    buy_strategy, sell_strategy = np.array_split(strategy, 2)
    strategy_df = pd.DataFrame(
        zip(toolbox.get_features_columns(), buy_strategy, sell_strategy),
        columns=["feature", "buy strategy weight", "sell strategy weight"],
    )

    dir_path = init_dump_dir(dirname_base)
    save_strategy(dir_path, strategy_df)
    save_logbook(dir_path, logbook)
    add_summary(dirname_base, {
        'path': dir_path,
        **save_simulation_params,
        'result': halloffame[0].fitness.values[0],
        'n_generations': generations,
        'execution_time': time() - start_time
    })


def eaGenerateUpdateWithRestartsAndFileDump(toolbox, nrestarts, maxngens, halloffame, stats, p, verbose=__debug__):
    for i in range(nrestarts):
        strategy = toolbox.generate_strategy()
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        logbook = tools.Logbook()
        logbook.header = ['restart', 'gen', 'nevals', 'sigma'] + stats.fields

        gen = 0
        stds = []
        halloffame.clear()
        start_time = time()

        while gen < maxngens:
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

            # Stop condition
            stds.append(np.std(fitnesses))
            if len(stds) > 3 and np.mean(stds[-3:]) < 1e-1:
                break

            # Increment generation number
            gen += 1

        dump_results('cmaes', toolbox, halloffame, logbook, gen, start_time, p)


def eaSimpleWithRestartsAndFileDump(toolbox, cxpb, mutpb, nrestarts, maxngens, stats, halloffame, p, verbose=__debug__):
    for i in range(nrestarts):
        population = toolbox.generate_population()

        logbook = tools.Logbook()
        logbook.header = ['restart', 'gen', 'nevals'] + stats.fields

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        halloffame.update(population)

        record = stats.compile(population)
        logbook.record(gen=0, nevals=len(invalid_ind), restart=i, **record)
        if verbose:
            print(logbook.stream)

        gen = 1
        maxs = []
        halloffame.clear()
        start_time = time()

        # Begin the generational process
        while gen < maxngens:
            # Select the next generation individuals
            offspring = toolbox.select(population, len(population))

            # Vary the pool of individuals
            offspring = varAnd(offspring, toolbox, cxpb, mutpb)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            halloffame.update(offspring)

            # Replace the current population by the offspring
            population[:] = offspring

            # Append the current generation statistics to the logbook
            record = stats.compile(population)
            logbook.record(gen=gen, nevals=len(invalid_ind), restart=i, **record)
            if verbose:
                print(logbook.stream)

            # Stop condition
            maxs.append(np.max(fitnesses))
            if len(maxs) > 1000 and np.min(maxs[-1000:]) == np.max(maxs[-1000:]):
                break

            # Increment generation number
            gen += 1

        dump_results('ea', toolbox, halloffame, logbook, gen, start_time, p)


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
):
    N = len(ta_features.columns) * 2

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("attr_uniform", random.uniform, -1, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_uniform, n=N)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("get_features_columns", lambda x: x, ta_features.columns)

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


def setup_stats():
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

    stats = setup_stats()
    hall_of_fame = tools.HallOfFame(1, compare_individuals)

    toolbox.register("generate_population", toolbox.population, n=pop_size)

    return toolbox, stats, hall_of_fame


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

    toolbox.register("generate_strategy", cma.Strategy, centroid=np.zeros(N), sigma=100, lambda_=lambda_)

    return toolbox, stats, hall_of_fame