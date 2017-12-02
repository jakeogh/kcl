#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kcl.sqlalchemy.get_engine import get_engine

def install_extensions(dbname):
    pg_uri = 'postgresql://postgres@localhost/'
    with get_engine(pg_uri+dbname, isolation_level='AUTOCOMMIT', echo=False).connect() as connection:
        connection.execute('CREATE EXTENSION uint;')

