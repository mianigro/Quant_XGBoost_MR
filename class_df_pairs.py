import pandas as pd
import numpy as np
from binance.client import Client
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json


class FindPairs:
    def __init__(self):
        self.trade_pairs = ["ETH"]
        self.df_array = []
        self.window = 50
        self.graphing = False

        # Data to populate
        self.data_df = None
        self.betas = None
        self.train_data = None
        self.x = None
        self.y = None

        # Get beta value from the local file
        self.determine_betas()

    # Finds the values of beta from our research JSON file
    def determine_betas(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "Notebooks/analysis_values.json")

        with open(file_path, "r") as f:
            self.betas = json.load(f)

    # Get data from local file for testing
    def use_data(self):
        self.data_df = pd.read_csv("ETH_BTC_test.csv").drop("Unnamed: 0", axis=1)
        self.df_array.append(self.data_df)

    # Get data from API
    def run_pairs(self):
        for item in self.trade_pairs:
            self.feature_gen(item)
            today = datetime.today()
            self.df_array.append(self.data_df)
            print(f"{today} - Instrument: {item}/BTC - Success")

    # Feature generation
    def feature_gen(self, pair1, pair2="BTC"):
        self.data_df = pd.DataFrame(
            columns=[pair1, pair2, "Coint Spread", "Mean",
                     "STD", "Z-Score", "Beta"])

        # Build df for train or test data, this will determine the length of time sampled
        if not self.train_data:
            pair_1, list_1 = self.get_history(pair1)
            pair_2, list_2 = self.get_history(pair2)
            self.data_df = pd.concat([pair_1, pair_2], axis=1)
        else:
            pair_1, list_1 = self.get_history_train(pair1)
            pair_2, list_2 = self.get_history_train(pair2)
            self.data_df = pd.concat([pair_1, pair_2], axis=1)

        # Generate cointegration columns
        self.x = np.log(self.data_df[f"{pair1} Close"])
        self.y = np.log(self.data_df[f"{pair2} Close"])
        self.data_df["Beta"] = self.betas[pair1][1]
        self.data_df["Coint Spread"] = self.y - self.betas[pair1][1] * self.x

        # Generate statistical information
        self.find_stats()

        # Save the train or test df into a local csv
        if self.train_data:
            self.data_df.to_csv(f"ETH_BTC_train.csv")
        else:
            self.data_df.to_csv(f"ETH_BTC_test.csv")

    # Generates statistical information for the data
    def find_stats(self):
        self.data_df["Mean"] = self.data_df["Coint Spread"].rolling(window=self.window).mean()
        self.data_df["STD"] = self.data_df["Coint Spread"].rolling(window=self.window).std()
        self.data_df["Z-Score"] = (self.data_df["Coint Spread"] - self.data_df["Mean"]) / self.data_df["STD"]
        self.data_df["Z-Score Lag 1"] = self.data_df["Z-Score"].shift(1)
        self.data_df["Z-Score Lag 2"] = self.data_df["Z-Score"].shift(2)
        self.data_df = self.data_df.dropna()

        if self.graphing:
            plt.plot(self.data_df["Z-Score"])
            plt.title("Z-Score over time for ETH vs BTC")
            plt.xlabel("Timestamps")
            plt.ylabel("Z-Score")
            plt.savefig('z-score.png')
            plt.show()

    # API to pull testing data - 2 months
    def get_history(self, instrument):
        key = os.getenv('KEY')
        secret = os.getenv('SECRET')
        client_history = Client(key, secret)

        k_lines = client_history.get_historical_klines(
            f"{instrument}AUD",
            Client.KLINE_INTERVAL_5MINUTE,
            "2 month ago UTC")

        df = pd.DataFrame(
            k_lines,
            columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                     "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                     "Taker buy quote asset volume", "Ignore"])

        df_out = pd.DataFrame()
        df_out[f"{instrument} Close"] = df["Close"].astype("float64")

        # Make lags
        df_lags, lag_list = self.make_lag_features(df_out, instrument)

        return df_lags, lag_list

    # API to pull training data - 2 years
    def get_history_train(self, instrument):
        key = os.getenv('KEY')
        secret = os.getenv('SECRET')
        client_history = Client(key, secret)

        k_lines = client_history.get_historical_klines(
            f"{instrument}AUD",
            Client.KLINE_INTERVAL_5MINUTE,
            "1 Jan 2021", "1 Jan 2023")

        df = pd.DataFrame(
            k_lines,
            columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                     "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                     "Taker buy quote asset volume", "Ignore"])

        df_out = pd.DataFrame()
        df_out[f"{instrument} Close"] = df["Close"].astype("float64")
        df_out[f"{instrument} Volume"] = df["Volume"].astype("float64")

        # Make lags
        df_lags, lag_list = self.make_lag_features(df_out, instrument)

        return df_lags, lag_list

    # Generating the lag features for the log of the prices
    def make_lag_features(self, df_in, instrument):
        # Setup list for lag feature names
        n = 30
        lag_list = [f"{instrument} Close"]
        # Loop through the amount of lag features needed to generate lags
        for x in range(1, n + 1):
            df_in[f"{instrument} Close_{x}"] = df_in[f"{instrument} Close"].shift(x)
            df_in[f"{instrument} Close_{x}"] = np.log(df_in[f"{instrument} Close_{x}"])
            lag_list.append(f"{instrument} Close_{x}")

        return df_in, lag_list
