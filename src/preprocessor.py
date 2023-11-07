"""
OBJECTIVE OF THIS MODULE
------------------------
Module to preprocess and clean the fetched data.
"""
import math

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def treat_missing_data(df):
    # If a value is missing, fill it with the previous value
    df = df.fillna(method="ffill")
    return df

def prepare_train_test_sets(df, train_size, rolling_window):
    if not 0 < train_size < 1:
        raise ValueError("Argument 'train_size' must be a value between 0 and 1")
    df = treat_missing_data(df)
    close_prices = df["close"].to_numpy()
    # We start with the train set
    training_data_len = int(round(len(close_prices) * train_size, 0))
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_data = close_prices[0:training_data_len]
    train_data = scaler.fit_transform(train_data.reshape(-1, 1))

    x_train = np.empty((0, rolling_window))
    y_train = train_data[rolling_window:, 0]

    for i in range(rolling_window, len(train_data)):
        x_train = np.vstack((x_train, train_data[i - rolling_window : i, 0]))

    # Adding a third dimension as a requirement from TensorFlow
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # Now, let's proceed with the test set
    # We subtract 60 because to output the first prediction on test
    # we need data on the 60 last close prices
    test_data = close_prices[training_data_len - rolling_window :]
    test_data = scaler.transform(test_data.reshape(-1, 1))

    x_test = np.empty((0, rolling_window))
    y_test = test_data[rolling_window:, 0]

    for i in range(rolling_window, len(test_data)):
        x_test = np.vstack((x_test, test_data[i - rolling_window : i, 0]))

    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
