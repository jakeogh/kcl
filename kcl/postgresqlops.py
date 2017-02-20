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

