from class_df_pairs import FindPairs
from class_api_trader import BinanceClass
from class_database_log import DatabaseLedger
from make_decision import make_decision
from datetime import datetime
import math
import numpy as np


def run_quant():
    # Load classes
    pair_data = FindPairs()
    binance_api = BinanceClass()
    db_ledger = DatabaseLedger()

    # Set constraints
    pair_data.train_data = False
    use_ml = True
    limit_trades = False
    gen_data = False

    # Generate data or use local testing data
    if gen_data:
        pair_data.run_pairs()
    else:
        pair_data.use_data()

    # Go through df to run strategy - This is done for each trading pair
    for df in pair_data.df_array:
        # Setup dataframe columns in order
        df = df.reindex(['ETH Close', 'BTC Close', 'Coint Spread', 'Mean', 'STD', 'Z-Score', 'ETH Volume', 'BTC Volume',
                         'Z-Score Lag 1', 'Z-Score Lag 2',
                         'ETH Close_1', 'ETH Close_2', 'ETH Close_3', 'ETH Close_4',
                         'ETH Close_5', 'ETH Close_6', 'ETH Close_7', 'ETH Close_8',
                         'ETH Close_9', 'ETH Close_10', 'ETH Close_11', 'ETH Close_12',
                         'ETH Close_13', 'ETH Close_14', 'ETH Close_15', 'ETH Close_16',
                         'ETH Close_17', 'ETH Close_18', 'ETH Close_19', 'ETH Close_20',
                         'ETH Close_21', 'ETH Close_22', 'ETH Close_23', 'ETH Close_24',
                         'ETH Close_25', 'ETH Close_26', 'ETH Close_27', 'ETH Close_28',
                         'ETH Close_29', 'ETH Close_30', 'BTC Close_1',
                         'BTC Close_2', 'BTC Close_3', 'BTC Close_4', 'BTC Close_5',
                         'BTC Close_6', 'BTC Close_7', 'BTC Close_8', 'BTC Close_9',
                         'BTC Close_10', 'BTC Close_11', 'BTC Close_12', 'BTC Close_13',
                         'BTC Close_14', 'BTC Close_15', 'BTC Close_16', 'BTC Close_17',
                         'BTC Close_18', 'BTC Close_19', 'BTC Close_20', 'BTC Close_21',
                         'BTC Close_22', 'BTC Close_23', 'BTC Close_24', 'BTC Close_25',
                         'BTC Close_26', 'BTC Close_27', 'BTC Close_28', 'BTC Close_29',
                         'BTC Close_30'], axis=1)

        # Loop each line in the df, this will go line by line and is done for training and testing,
        # live deployment uses x=-1 as you only want to use the current value
        for x in range(1, len(df)):
            # Extracts data row by row for back testing
            pair_1, pair_2, spread, mean, std, zscore, eth_vol, btc_vol, zscore_1, zscore_2, *lag_list = df.iloc[x-1]

            # Extracting pair information and reporting it
            pair_1_name = "ETH"
            pair_2_name = "BTC"
            pair_name = f"{pair_1_name}{pair_2_name}"
            db_ledger.add_activity(pair_name, zscore, pair_1, pair_2)
            time_now = datetime.today()
            print(f"{time_now} - Pair: {pair_name[:3]}/{pair_name[3:]} - Z-Score: {round(zscore, 5)}")

            # Check for open trades in the database
            trade_actions = db_ledger.find_open_trades(pair_name)

            # Closing any open trades if needed based on the Z-Score
            if trade_actions:
                print(f"{time_now} - Open Trades: {trade_actions}")
                item_trade = trade_actions[0][1]

                if item_trade == "Long":
                    if zscore <= 0.2:
                        db_ledger.close_trade(pair_name, pair_1, pair_2)

                elif item_trade == "Short":
                    if zscore >= -0.2:
                        db_ledger.close_trade(pair_name, pair_1, pair_2)

            # Generates a trading signal
            trade_option = make_decision(
                np.log(pair_1), np.log(pair_2), spread, mean, std, zscore, lag_list, zscore_1, zscore_2, eth_vol, btc_vol, use_ml)

            # Actions trading signal, checks bank balance and trade counts and executes the trade
            if trade_option:
                # Trade count limits
                if not limit_trades:
                    trade_counts = {"ETH": 999999999999999999999999999999}
                else:
                    trade_counts = {"ETH": 4}

                # Check trade count limit is not reached
                if len(trade_actions) < trade_counts[pair_1_name]:
                    # Mock bank balance
                    balances = {"ETH": 999999999999999999999999999999, "BTC": 999999999999999999999999999999}

                    # Set unit amount based on current price and determined trade size
                    pair_1_trade = round(
                        binance_api.trade_value / pair_1,
                        binance_api.rounding[pair_1_name])
                    pair_2_trade = round(
                        binance_api.trade_value / pair_2,
                        binance_api.rounding[pair_2_name])

                    # Makes sure balance is sufficient
                    if pair_1_trade > balances[pair_1_name]:
                        pair_1_trade = math.floor(balances[pair_1_name] * 1000 * 0.95) / 1000
                    if pair_2_trade > balances[pair_2_name]:
                        pair_2_trade = math.floor(balances[pair_2_name] * 1000 * 0.95) / 1000

                    # Make the trade
                    if trade_option == "Long":
                        print(f"{time_now} - Open long position - {pair_1_name}/{pair_2_name}")
                        binance_api.long_trade()
                        db_ledger.add_trade(
                            pair_name,
                            trade_option,
                            pair_1_trade,
                            pair_2_trade,
                            pair_1,
                            pair_2,
                            eth_vol,
                            btc_vol)

                    elif trade_option == "Short":
                        print(f"{time_now} - Open short position - {pair_1_name}/{pair_2_name}")
                        binance_api.short_trade()
                        db_ledger.add_trade(
                            pair_name,
                            trade_option,
                            pair_1_trade,
                            pair_2_trade,
                            pair_1,
                            pair_2,
                            eth_vol,
                            btc_vol)
