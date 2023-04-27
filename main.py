from run_script import run_quant
from make_table import make_table_func
import os


def main():
    delete_db = True

    if delete_db:
        if os.path.isfile("ledger.db"):
            os.remove("ledger.db")
            make_table_func()
        else:
            make_table_func()

    else:
        if not os.path.isfile("ledger.db"):
            make_table_func()

    run_quant()


if __name__ == "__main__":
    main()
