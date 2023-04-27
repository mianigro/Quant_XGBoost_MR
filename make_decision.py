import numpy as np
import os
from xgboost import XGBClassifier


def make_decision(log_pair1,
                  log_pair2,
                  spread,
                  mean,
                  std,
                  z_score,
                  lag_list,
                  zscore_1,
                  zscore_2,
                  eth_vol,
                  btc_vol,
                  use_ml):

    # Get location of model
    file_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(file_dir, "Notebooks/eth_btc.model")

    if z_score >= 2.0:
        # Using ML or not
        if use_ml:
            # Extract information and make a prediction from the model
            in_list = [log_pair1, log_pair2, spread, mean, std, eth_vol, btc_vol, zscore_1, zscore_2]
            for item in lag_list:
                in_list.append(float(item))

            model = XGBClassifier()
            model.load_model(file_path)
            data_in = np.array([in_list])
            is_profit = model.predict(data_in)

        else:
            # Uses trading signal based on z-score only
            is_profit = 1

        # Set trade as long
        if is_profit == 1:
            trade_option = "Long"

        else:
            trade_option = None

    elif z_score <= -2.0:
        # Using ML or not
        if use_ml:
            # Extract information and make a prediction from the model
            in_list = [log_pair1, log_pair2, spread, mean, std, eth_vol, btc_vol, zscore_1, zscore_2]
            for item in lag_list:
                in_list.append(float(item))

            model = XGBClassifier()
            model.load_model(file_path)
            data_in = np.array([in_list])
            is_profit = model.predict(data_in)

        else:
            # Uses trading signal based on z-score only
            is_profit = 1

        # Set trade as short
        if is_profit == 1:
            trade_option = "Short"

        else:
            trade_option = None

    else:
        trade_option = None

    # Return either long/short/None
    return trade_option

