class BinanceClass:
    def __init__(self):
        self.trade_value = 250
        self.rounding = {"ETH": 3, "BTC": 3, "AUD": 2}

    def long_trade(self):
        print("Sell BTC")
        print("Buy ETH")

    def short_trade(self):
        print("Buy BTC")
        print("sell ETH")