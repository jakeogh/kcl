#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
from kcl.postgresqlops import delete_database
import os


def run_test(db_test, engine):
    print(db_test)
    with engine.connect() as connection:
        answer = connection.execute(db_test[0])
        for row in answer:
            try:
                assert row[0] == db_test[1]
            except AssertionError as e:
                print("\nAssertionError on db test:", db_test[0])
                print("row[0] != db_test[0]:\n", row[0], "!=", db_test[1])
                raise e

def check_db_result(config, db_result, session, orm_result=False):
    ENGINE = get_engine(database=config.timestamp_database)
    tables = set(ENGINE.table_names())
    print("tables:", tables)
    assert tables
    for db_test in db_result:
        run_test(db_test=db_test, engine=ENGINE)

        db_test_table = db_test[0].split()[-1].split(';')[0]
        #print("db_test_table:", db_test_table)
        tables.remove(db_test_table)

    if tables:
        print("Missed table test(s):", tables)
        for table in tables:
            constructed_test = "'select COUNT(*) from %s;'" % table
            run_test(db_test=(constructed_test, 0), engine=ENGINE)
            tables.remove(table)

    assert not tables

    ENGINE.dispose()
    session.close()
    if not os.getenv("iridb_keep_test_databases"):
        delete_database(database=config.timestamp_database)
    else:
        print("skipped delete_database on:", config.timestamp_database)
