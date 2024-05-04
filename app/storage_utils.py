import os
import time
import csv
import numpy as np
import pandas as pd


STORAGE_DIR_PATH = './storage/'


def init_dump_dir(dirname_base):
    time_str = time.strftime("%Y-%m-%d_%H-%M-%S")
    dir_path = os.path.join(STORAGE_DIR_PATH, f'{dirname_base}_{time_str}')
    os.mkdir(dir_path)
    return dir_path


def print_file(file_path):
    with open(file_path, 'r') as f:
        print(f.read())


def save_features(dir_path, features_df):
    file_path = os.path.join(dir_path, 'features.csv')
    print(features_df)
    features_df.to_csv(file_path)
    return file_path


def save_logbook(dir_path, logbook):
    file_path = os.path.join(dir_path, 'logbook.csv')
    field_names = logbook[0].keys()
    with open(file_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=field_names)
        w.writeheader()
        for r in logbook:
            for k, v in r.items():
                if type(v) is list:
                    r[k] = v[0]
            w.writerow(r)
    return file_path


def load_logbook(dir_path):
    file_path = os.path.join(dir_path, 'logbook.csv')
    df = pd.read_csv(file_path)
    output_list = df.to_dict(orient='records')
    output_list = [{key: value for key, value in d.items() if key in ['gen', 'nevals', 'avg', 'std', 'min', 'max']} for d in output_list]
    return output_list


def load_strategy(dir_path):
    file_path = os.path.join(dir_path, 'features.csv')
    features_df = pd.read_csv(file_path)
    return np.concatenate([features_df['buy strategy weight'].values.reshape(-1, 1),
                           features_df['sell strategy weight'].values.reshape(-1, 1)], axis=0).flatten()
