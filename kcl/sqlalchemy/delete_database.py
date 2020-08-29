#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
#from kcl.printops import eprint
from icecream import ic

def delete_database(database):
    ic(database)
    dbpath = 'postgres://postgres@localhost/'
    assert database.startswith(dbpath)
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    ic('DROP DATABASE:', database)
    with create_engine(pg_dbpath, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute("COMMIT") # end the transaction, technically not nessary with AUTOCOMMIT
        connection.execute('DROP DATABASE ' + dbname)

