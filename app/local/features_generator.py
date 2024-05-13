import inspect
import random

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from preprocessing import load_data


def generate_features(module):
    random.seed(420)
    stock_data, ta_features, preview = load_data("./data/wig_d.csv")
    constructors = get_constructors(module)
    instances = inject_params(constructors, stock_data)
    features = retrieve_features(instances)
    return features


def normalize(df):
    columns = list(df.columns)
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def append_features(features, ta_features):
    series = []
    for feature_name, feature_vals in features.items():
        series.append(pd.Series(feature_vals, name=feature_name))
    df = pd.concat(series, axis=1)
    df = df.tail(-365)
    df = pd.concat([ta_features, df], axis=1)
    return df


def get_constructors(module):
    # Get all class names defined in the module
    class_names = [name for name in dir(module) if isinstance(getattr(module, name), type)]
    constructors = []
    # Print constructors for each class with their arguments
    for class_name in class_names:
        class_ = getattr(module, class_name)
        # Check if it's a class (not a module or function)
        if isinstance(class_, type):
            # Check if the class has a __init__ method
            if hasattr(class_, '__init__'):
                # Get the constructor signature
                init_signature = inspect.signature(getattr(class_, '__init__'))
                full_class_name = f'{module.__name__}.{class_name}'
                constructor = (class_, init_signature)
                constructors.append(constructor)
                # print(constructor)
            else:
                # print(f"Class {class_name} does not have a constructor (__init__ method)")
                pass
    return constructors


def inject_params(constructors, stock_data):
    instances = dict()
    for constructor in constructors:
        init_signature = constructor[1]
        to_inject = dict()
        for param in init_signature.parameters.values():
            if param.name in ('self', 'args', 'kwargs'):
                continue
            if param.name in stock_data:
                to_inject[param.name] = stock_data[param.name]
            else:
                _type = type(param.default)
                value = None
                if _type is int or param.name == 'window':
                    value = random.randint(1, 100)
                if _type is float:
                    value = random.uniform(1, 100)
                if _type is bool:
                    value = False
                to_inject[param.name] = value
        instance = constructor[0]() if len(init_signature.parameters.values()) == 1 else constructor[0](**to_inject)
        instances['GENERATED_' + constructor[0].__name__] = instance
    return instances


def retrieve_features(instances):
    features = dict()
    for feature_name, instance in instances.items():
        if feature_name != 'GENERATED_VolumeWeightedAveragePrice':
            method_names = [m for m in dir(instance) if m[0] != '_']
            for method_name in method_names:
                method = getattr(instance, method_name)
                feature_vals = method()
                # print(feature_name, feature_vals.isna().sum())
                if feature_vals.isna().sum() < 365:
                    features[feature_name] = feature_vals
            if len(method_names) == 0:
                continue
    return features
