#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# use from sqlalchemy_utils.functions import create_database instead

from sqlalchemy import create_engine
from kcl.printops import eprint

def create_databas_old(database):
    dbpath = 'postgresql://postgres@localhost/'
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    eprint("CREATE DATABASE:", database)
    with create_engine(pg_dbpath, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute("COMMIT") # end the transaction, technically not nessary with AUTOCOMMIT
        connection.execute('CREATE DATABASE ' + dbname)
