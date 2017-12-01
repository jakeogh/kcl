#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from kcl.printops import eprint
from kcl.sqlalchemy.create_session import create_session

def delete_database(database):
    dbpath = 'postgresql://postgres@localhost/'
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    eprint("DROP DATABASE:", database)
    with create_engine(pg_dbpath, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('DROP DATABASE ' + dbname)

def create_database(database):
    dbpath = 'postgresql://postgres@localhost/'
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    eprint("CREATE DATABASE:", database)
    with create_engine(pg_dbpath, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE DATABASE ' + dbname)

def create_database_and_tables(database, schema):
    create_database(database=database)
    create_tables(database=database, schema=schema)

def install_extensions(dbname):
    with create_engine('postgresql://postgres@localhost/' + dbname,
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE EXTENSION uint;')

def delete_and_recreate_database(database):
    try:
        delete_database(database=database)
    except ProgrammingError:
            pass #db didnt exist
    finally:
        create_database(database=database)
        #install_extensions(dbname)

def start_database():
    os.system('sudo /etc/init.d/postgresql-9.6 start')

def create_tables(database, schema):
    #temp_engine = create_engine("postgres://postgres@localhost/" + dbname, echo=False)
    temp_engine = create_engine(database, echo=False)
    schema.metadata.create_all(temp_engine)

def delete_and_recreate_database_and_session(database, schema):
    delete_and_recreate_database(database=database)
    create_tables(database=database, schema=schema)
    return create_session(database=database)

def get_engine(database):
    assert isinstance(database, str)
    engine = create_engine(database, echo=False)
    return engine
