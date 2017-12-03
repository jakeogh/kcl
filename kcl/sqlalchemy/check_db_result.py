#!/usr/bin/env python3
#from kcl.sqlalchemy.delete_database import delete_database
from sqlalchemy_utils.functions import drop_database
from kcl.printops import eprint
from kcl.sqlalchemy.get_engine import get_engine
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

def check_db_result(config, db_result, orm_result_list=False):
    #ENGINE = session.bind
    ENGINE = get_engine(config.timestamp_database)
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
                if orm_result_list:
                    for result in orm_result_list:
                        orm_result = result['orm_result']
                        for key in orm_result.keys():
                            if orm_result[key]:
                                hash_set.append(orm_result[key])

                    hash_set = set(hash_set)

            constructed_test = 'select COUNT(*) from %s;' % table

            run_test(db_test=(constructed_test, len(hash_set)), engine=ENGINE) #hash_set is usually len() == 0 so it works for the default case of 0
            tables.remove(table)

    #eprint("remaning tables:", tables)
    assert len(tables) == 0

    ENGINE.dispose()
    if not os.getenv("iridb_keep_test_databases"):
        drop_database(config.timestamp_database)
    else:
        print("skipped delete_database on:", config.timestamp_database)
