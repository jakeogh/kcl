#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
import click

@click.command()
@click.argument("database", nargs=1)
def list_tables(database):
    ENGINE = get_engine(database=database)
    tables = set(ENGINE.table_names())
    print("tables:", tables)
    assert tables

