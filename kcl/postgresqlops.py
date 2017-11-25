#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
#from psycopg2 import ProgrammingError
from sqlalchemy.exc import ProgrammingError
from .printops import eprint

def drop_database(database):
    dbpath = 'postgresql://postgres@localhost/'
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    eprint("dropping database:", dbname)
    #with create_engine('postgresql://postgres@localhost/postgres',
    with create_engine(pg_dbpath, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('DROP DATABASE ' + dbname)

def create_database(database):
    dbpath = 'postgresql://postgres@localhost/'
    pg_dbpath = dbpath + 'postgres'
    assert dbpath in database
    dbname = database.split(dbpath)[-1]
    eprint("CREATE DATABASE:", dbname)
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
        drop_database(database=database)
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

def create_session(database, multithread=False):
    if not multithread:
        #ENGINE = create_engine("postgres://postgres@localhost/" + dbname,
        engine = create_engine(database, echo=False, poolclass=NullPool)
        session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    else:
        engine = create_engine(database, echo=False, pool_size=20, max_overflow=100)
        session = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
    return session


def delete_and_recreate_database_and_session(database, schema):
    delete_and_recreate_database(database=database)
    create_tables(database=database, schema=schema)
    return create_session(database=database)

def get_engine(database):
    assert isinstance(database, str)
    engine = create_engine(database, echo=False)
    return engine


