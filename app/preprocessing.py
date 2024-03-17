import pandas as pd
import ta

from sklearn.preprocessing import MinMaxScaler
from ta.utils import dropna


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = dropna(df)
    df = ta.add_all_ta_features(
        df, "open", "high", "low", "close", "volume"
    )
    df = df.drop(columns=['trend_psar_up', 'trend_psar_down'])  # TODO: merge or something
    df = df.tail(-100)
    columns = list(df.columns)[6:]
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df
