#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

def drop_database(dbname):
    with create_engine('postgresql://postgres@localhost/postgres',
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('DROP DATABASE ' + dbname)

def create_database(dbname):
    with create_engine('postgresql://postgres@localhost/postgres',
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE DATABASE ' + dbname)

def install_extensions(dbname):
    with create_engine('postgresql://postgres@localhost/' + dbname,
                       isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE EXTENSION uint;')

def delete_and_recreate_database(dbname):
    try:
        drop_database(dbname)
    except:
        pass
    finally:
        create_database(dbname)
        install_extensions(dbname)

def start_database():
    os.system('sudo /etc/init.d/postgresql-9.6 start')

def create_tables(dbname, schema):
    temp_engine = create_engine("postgres://postgres@localhost/" + dbname, echo=False)
    # Base.metadata.create_all(temp_engine)
    schema.metadata.create_all(temp_engine)

def create_database_and_session(database, schema):
    delete_and_recreate_database(database)
    create_tables(database, schema)
    return create_session()

