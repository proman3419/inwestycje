from preprocessing import preprocess_data
from setup import setup_cmaes, eaGenerateUpdateWithRestartsAndFileDump
import argparse
from storage_utils import set_storage_dir_path


def init_args():
    arg_parser = argparse.ArgumentParser(
        description='''-- DEFAULTS --
CMAES algorithm parameters:
LAMBDA = args.LAMBDA
SIGMA = 1000

# Simulation parameters:
N_RESTARTS = 1000
MAX_N_GENERATIONS = 10000
INITIAL_MONEY = 1000
COMMISSION = 0
''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    arg_parser.add_argument('--LAMBDA', type=int, default=150)
    arg_parser.add_argument('--SIGMA', type=int, default=1000)
    arg_parser.add_argument('--N_RESTARTS', type=int, default=1000)
    arg_parser.add_argument('--MAX_N_GENERATIONS', type=int, default=10000)
    arg_parser.add_argument('--INITIAL_MONEY', type=int, default=1000)
    arg_parser.add_argument('--COMMISSION', type=float, default=0)
    arg_parser.add_argument('--STORAGE_DIRNAME_BASE', type=str, default='')
    arg_parser.add_argument('--DATASET', type=str, default='data/wig_d.csv')

    return arg_parser.parse_args()


args = init_args()

set_storage_dir_path(args.STORAGE_DIRNAME_BASE)

stock_data, ta_features, _ = preprocess_data("data/pkn_d.csv")

toolbox, stats, hall_of_fame = setup_cmaes(
    stock_data,
    ta_features,
    args.LAMBDA,
    args.SIGMA,
    args.INITIAL_MONEY,
    args.COMMISSION,
)

eaGenerateUpdateWithRestartsAndFileDump(
    toolbox=toolbox,
    nrestarts=args.N_RESTARTS,
    maxngens=args.MAX_N_GENERATIONS,
    stats=stats,
    halloffame=hall_of_fame,
    p={"initial_money": args.INITIAL_MONEY, "commision": args.COMMISSION},
    verbose=True,
)
