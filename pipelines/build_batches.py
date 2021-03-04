import os
from typing import List, Dict, Tuple
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
import yaml
import os
import pandas as pd

# Get all config values and hyperparameters
with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def _load_from_file(dataset:str) -> List[List[float]]:
    """
    Read raw csv closing price data into lists, filling in empty values with
    the closing price of the previous day.
    :param dataset: name of the security whose price history will be loaded
    :return: lists corresponding to datasets for train, valid, and test
    """
    dataset = dataset.lower()
    if dataset not in config["ALLOWED_DATASETS"]:
        raise ValueError(f'Dataset type {dataset} not allowed')
    else:
        files = {}
        for file in os.listdir(config["CLEAN_DATA_PATH"]):
            if not file.startswith(dataset):
                continue

            ds = file.split('.')[1]

            with open(os.path.join(config["CLEAN_DATA_PATH"], file), 'r') as f:
                files[ds] = [float(x) for x in f.read().split(',')]

        return [files[k] for k in ['train', 'valid', 'test']]

def _build_episode(prices:List[float]) -> List[Tuple[Tensor, Tensor, float, float, float]]:
    """
    Convert raw prices into requisite data for one episode
    :param prices: raw float values from file
    :return: list of tuples consisting of (state, next state, price, previous price, initial price)
    """
    episode = []
    today_prices = torch.Tensor(prices[1:])
    yesterday_prices = torch.Tensor(prices[:-1])
    states = today_prices - yesterday_prices

    for i in range(len(states) - config["LOOKBACK"]):
        state = states[i:config["LOOKBACK"]+i]
        next_state = states[i+1:config["LOOKBACK"]+i+1]
        price = today_prices[config["LOOKBACK"] + i - 1]
        prev_price = yesterday_prices[config["LOOKBACK"] + i - 1]
        sample = (state, next_state, price, prev_price, today_prices[i])
        # price = today_prices[i]
        # prev_price = yesterday_prices[i]
        # sample = (state, next_state, price, prev_price, today_prices[0])
        episode.append(sample)
    return episode


def get_episode(dataset:str) -> List[List[Tuple[Tensor, Tensor, float, float, float]]]:
    """
    Each episode sample contains (state, next_state, price, prev_price, init_price) where
        state       p_t - p_{t-1} for t-199 to t where p_t is the closing price
                    on day t
        next_state  identical to state but shifted forward by one day
                    e.g. next_state[0] == state[1]
        price       closing price for day t
        prev_price  closing price for day t-1
        init_price  closing price for day t-n
    :param dataset: which security price history will be loaded
    :return: list of samples for each trading day in episode
    """
    datasets = _load_from_file(dataset)
    return [_build_episode(ds) for ds in datasets]


def load_prices(index: str, symbol: str):
    path = config["STOCK_DATA_PATH"]
    file = f"{index}/{symbol}.csv"
    df = pd.read_csv(os.path.join(path, file))
    # first, second columns to datetime, float64
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df[df.columns[1]] = df[df.columns[1]].astype('float64')

    return df
