#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
#from psycopg2 import ProgrammingError
from sqlalchemy.exc import ProgrammingError

def drop_database(dbname):
    with create_engine('postgresql://postgres@localhost/postgres',
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('DROP DATABASE ' + dbname)

def create_database(dbname):
    with create_engine('postgresql://postgres@localhost/postgres',
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE DATABASE ' + dbname)

def create_database_and_tables(dbname, schema):
    create_database(dbname=dbname)
    create_tables(dbname=dbname, schema=schema)

def install_extensions(dbname):
    with create_engine('postgresql://postgres@localhost/' + dbname,
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE EXTENSION uint;')


def delete_and_recreate_database(dbname):
    try:
        drop_database(dbname)
    except ProgrammingError:
            pass #db didnt exist
    finally:
        create_database(dbname)
        #install_extensions(dbname)

def start_database():
    os.system('sudo /etc/init.d/postgresql-9.6 start')

def create_tables(dbname, schema):
    temp_engine = create_engine("postgres://postgres@localhost/" + dbname, echo=False)
    schema.metadata.create_all(temp_engine)

def create_session(dbname, multithread=False):
    if not multithread:
        ENGINE = create_engine("postgres://postgres@localhost/" + dbname,
                               echo=False, poolclass=NullPool)
        Session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False, bind=ENGINE))
    else:
        ENGINE = create_engine("postgres://postgres@localhost/" + dbname,
                               echo=False, pool_size=20, max_overflow=100)
        Session = scoped_session(sessionmaker(autocommit=True,
                                              autoflush=False, bind=ENGINE))
    return Session


def delete_and_recreate_database_and_session(dbname, schema):
    delete_and_recreate_database(dbname)
    create_tables(dbname, schema)
    return create_session(dbname)

def get_engine(dbpath):
    assert isinstance(dbpath, str)
    engine = create_engine(dbpath, echo=False)
    return engine


