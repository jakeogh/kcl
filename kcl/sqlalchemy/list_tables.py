#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
import os

def list_tables(dbpath):
    ENGINE = get_engine(dbpath=dbpath)
    tables = set(ENGINE.table_names())
    print("tables:", tables)
    assert tables

