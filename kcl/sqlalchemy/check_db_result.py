#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
from kcl.postgresqlops import delete_database
from kcl.printops import eprint
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
    tables = list(ENGINE.table_names())
    print("tables:", tables)
    assert tables
    for db_test in db_result:
        run_test(db_test=db_test, engine=ENGINE)

        db_test_table = db_test[0].split()[-1].split(';')[0]
        #print("db_test_table:", db_test_table)
        tables.remove(db_test_table)


    unchecked_tables = list(tables)
    if unchecked_tables:
        print("constructing missed table test(s) for:", tables)
        for table in unchecked_tables:
            hash_set = []
            if table == 'hash':
                if orm_result:
                    for result in orm_result:
                        for key in result.keys():
                            if result[key]:
                                hash_set.append(result[key])

                    hash_set = set(hash_set)

            constructed_test = 'select COUNT(*) from %s;' % table

            run_test(db_test=(constructed_test, len(hash_set)), engine=ENGINE) #hash_set is usually len() == 0 so it works for the default case of 0
            tables.remove(table)

    #eprint("remaning tables:", tables)
    assert len(tables) == 0

    ENGINE.dispose()
    session.close()
    if not os.getenv("iridb_keep_test_databases"):
        delete_database(database=config.timestamp_database)
    else:
        print("skipped delete_database on:", config.timestamp_database)
