#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kcl.printops import eprint
from kcl.sqlalchemy.create_database import create_database
from kcl.sqlalchemy.create_tables import create_tables

def create_database_and_tables(database, schema):
    create_database(database=database)
    create_tables(database=database, schema=schema)

