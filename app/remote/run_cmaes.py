from preprocessing import preprocess_data
from setup import setup_cmaes, eaGenerateUpdateWithRestartsAndFileDump

stock_data, ta_features, _ = preprocess_data("./wig_d.csv")

# CMAES algorithm parameters:
LAMBDA = 150

# Simulation parameters:
N_RESTARTS = 1000
MAX_N_GENERATIONS = 10000
INITIAL_MONEY = 1000
COMMISSION = 0 # 0.0001 # 0.01%

toolbox, stats, hall_of_fame = setup_cmaes(
    stock_data,
    ta_features,
    LAMBDA,
    INITIAL_MONEY,
    COMMISSION,
)

eaGenerateUpdateWithRestartsAndFileDump(
    toolbox=toolbox,
    nrestarts=N_RESTARTS,
    maxngens=MAX_N_GENERATIONS,
    stats=stats,
    halloffame=hall_of_fame,
    p={"initial_money": INITIAL_MONEY, "commision": COMMISSION},
    verbose=True,
)
