#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
import click

@click.command()
@click.argument(dbpath, nargs=1)
def list_tables(dbpath):
    ENGINE = get_engine(dbpath=dbpath)
    tables = set(ENGINE.table_names())
    print("tables:", tables)
    assert tables

