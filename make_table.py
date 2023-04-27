from class_database_log import DatabaseLedger


def make_table_func():
    db_ledger = DatabaseLedger()
    db_ledger.make_table()
    db_ledger.make_table_log()
