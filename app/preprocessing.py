import pandas as pd
import numpy as np
import ta

from sklearn.preprocessing import MinMaxScaler
from ta.utils import dropna


def preprocess_data(path: str) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    stock_data, ta_features, preview = load_data(path)
    drop_highly_correlated(ta_features)
    return stock_data, ta_features, preview


def load_data(path: str) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    df = pd.read_csv(path, sep=";")
    df = dropna(df)
    df = ta.add_all_ta_features(
        df, "open", "high", "low", "close", "volume"
    )
    df = df.drop(columns=['trend_psar_up', 'trend_psar_down'])  # TODO: merge or something
    df = df.tail(-100)
    columns = list(df.columns)[6:]
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    stock_data = df.iloc[:, :6]
    ta_features = df.iloc[:, 6:]
    preview = pd.concat([stock_data, ta_features], axis=1)
    return stock_data, ta_features, preview


# https://stackoverflow.com/questions/29294983/how-to-calculate-correlation-between-all-columns-and-remove-highly-correlated-on
def drop_highly_correlated(df: pd.DataFrame, threshold=0.99) -> None:
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    df.drop(to_drop, axis=1, inplace=True)
