#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
from kcl.postgresqlops import drop_database
import os

def check_db_result(config, db_result, session):
    ENGINE = get_engine(dbpath=config.dbpath)
    tables = set(ENGINE.table_names())
    print("tables:", tables)
    assert tables
    for db_test in db_result:
        print(db_test)
        db_test_table = db_test[0].split()[-1].split(';')[0]
        #print("db_test_table:", db_test_table)
        tables.remove(db_test_table)
        with ENGINE.connect() as connection:
            answer = connection.execute(db_test[0])
            for row in answer:
                try:
                    assert row[0] == db_test[1]
                except AssertionError as e:
                    print("\nAssertionError on db test:", db_test[0])
                    print("row[0] != db_test[0]:\n", row[0], "!=", db_test[1])
                    raise e

    if tables:
        print("Missed table test(s):", tables)
    assert not tables

    ENGINE.dispose()
    session.close()
    if not os.getenv("iridb_keep_test_databases"):
        drop_database(dbname=config.dbname)
    else:
        print("skipped drop_database on:", config.dbname)
