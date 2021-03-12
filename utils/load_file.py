import os
import yaml
import pandas as pd
import numpy as np
from typing import Tuple
import torch

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

def index_prices(index_name:str):
    return component_prices(index_name, f'^{index_name.upper()}.csv')


def component_prices(index_name:str, component_name:str):
    filename = f'{component_name.upper()}.csv'
    path = os.path.join(config["STONK_PATH"], index_name, filename)
    with open(path, 'r') as f:
        lines = f.read().split('\n')[1:]
        lines = filter(lambda line: len(line) > 0, lines)

        try:
            lines = [float(x.split(',')[1]) for x in lines]
        except:
            print(component_name)

    return lines

def index_component_names(index_name:str):
    dir = os.path.join(config["STONK_PATH"], index_name)
    files = os.listdir(dir)
    files = map(lambda x: x[:-4], files)
    files = filter(lambda x: not x.startswith('^'), files)
    return list(files)

def load_index_prices(index_name:str):
    path = config["STONK_PATH"]
    df = pd.read_csv(os.path.join(path, 'index_data', f'{index_name}.csv'))
    df = df[df.columns[1]].astype('float64')
    return df.to_numpy()

def load_component_prices(index_name:str, split=True):
    component_names = index_component_names(index_name)
    prices = [component_prices(index_name, c) for c in component_names]

    if split:
        prices = [train_test_splits(p)[0] for p in prices]

    return torch.transpose(torch.tensor(prices), dim0=0, dim1=1)

def load_prices(index: str, symbol: str):
    path = config["STONK_PATH"]
    file = f"{index}/{symbol}.csv"
    df = pd.read_csv(os.path.join(path, file))
    # first, second columns to datetime, float64
    df = df[df.columns[1]].astype('float64')
    prices = df.to_numpy()
    return prices

def train_test_splits(prices: np.array) -> Tuple[np.array, np.array]:
    """
    Split prices into train, valid, test: 1/2, 1/6, 1/3
    :param prices:
    :return:
    """
    size = len(prices)
    train_idx = int(size*(2/3))

    train = prices[:train_idx]
    test = prices[train_idx:]

    return train, test


def load_relationship_info(type, index):
    path = os.path.join(config['STONK_PATH'], 'relationships', type, f'{index}.csv')
    return pd.read_csv(path)


if __name__ == '__main__':
    print(index_component_names('gspc'))