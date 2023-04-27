import sqlite3
import datetime
import os
import os.path


class DatabaseLedger:
    def __init__(self):
        self.conn = None
        self.c = None

    # Opens the database and sets the cursor
    def open_db(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "ledger.db")
        self.conn = sqlite3.connect(file_path)
        self.c = self.conn.cursor()

    # Makes ledger table if needed
    def make_table(self):
        self.open_db()
        self.c.execute("""CREATE TABLE tx_ledger (
            pair_name text,
            trade_type text,
            open_date date,
            close_date date,
            status text,
            units_1 numeric,
            units_2 numeric,
            pair_1_vol numeric,
            pair_2_vol numeric,
            pair_1_open numeric,
            pair_2_open numeric,
            pair_1_close numeric,
            pair_2_close numeric
            )""")

        self.conn.commit()
        self.conn.close()

    # Makes log table if needed
    def make_table_log(self):
        self.open_db()
        self.c.execute("""CREATE TABLE activity_log (
            pair_name text,
            z_score numeric,
            pair_1_price numeric,
            pair_2_price numeric,
            time_date date
            )""")

        self.conn.commit()
        self.conn.close()

    # Adding a trade to the database
    def add_trade(self, pair, trade_type, units_1, units_2, pair_1_open, pair_2_open, pair_1_vol, pair_2_vol):
        self.open_db()
        date_open = datetime.datetime.today()
        new_trade = (pair, trade_type, date_open, "", "OPEN", units_1, units_2, pair_1_vol, pair_2_vol, pair_1_open, pair_2_open, "", "")

        self.c.execute("""INSERT INTO tx_ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", new_trade)
        self.conn.commit()
        self.conn.close()

    # Finds the open trade and closes them
    def close_trade(self, pair, pair_1_close, pair_2_close):
        self.open_db()
        self.c = self.conn.cursor()
        date_close = datetime.datetime.today()

        self.c.execute(
            """UPDATE tx_ledger SET close_date = ? WHERE pair_name = ? AND status = 'OPEN' """, (date_close, pair))
        self.c.execute(
            """UPDATE tx_ledger SET pair_1_close = ? WHERE pair_name = ? AND status = 'OPEN' """, (pair_1_close, pair))
        self.c.execute(
            """UPDATE tx_ledger SET pair_2_close = ? WHERE pair_name = ? AND status = 'OPEN' """, (pair_2_close, pair))
        self.c.execute(
            """UPDATE tx_ledger SET status = ? WHERE pair_name = ? AND status = 'OPEN' """, ("CLOSED", pair))
        self.conn.commit()
        self.conn.close()

    # Find all the open trades and returns the info as a list
    def find_open_trades(self, pair):
        self.open_db()
        self.c = self.conn.cursor()
        self.c.execute("""SELECT * FROM tx_ledger WHERE pair_name = ? AND status = ? """, (pair, "OPEN"))
        items = self.c.fetchall()

        action_trades = []
        for item in items:
            # Structure of list is [pair, trade type, units_1, units_2]
            action_trades.append((item[0], item[1], item[5], item[6]))

        self.conn.commit()
        self.conn.close()

        return action_trades

    # Adding an activity to the database
    def add_activity(self, pair, z_score, pair_1, pair_2):
        self.open_db()
        date_open = datetime.datetime.today()
        new_entry = (pair, z_score, pair_1, pair_2, date_open)

        self.c.execute("""INSERT INTO activity_log VALUES (?, ?, ?, ?, ?)""", new_entry)
        self.conn.commit()
        self.conn.close()