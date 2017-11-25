#!/usr/bin/env python3
from kcl.postgresqlops import get_engine
from kcl.sqlalchemy.BaseMixin import BASE
from pprint import pprint
import click

@click.command()
@click.argument("database", nargs=1)
@click.option("--verbose", is_flag=True)
def list_tables(database, verbose):
    engine = get_engine(database=database)
    if verbose:
        BASE.metadata.reflect(engine)
        table_names = BASE.metadata.tables.keys()
        for table in table_names:
            pprint(BASE.metadata.tables[table])
    else:
        tables = engine.table_names()
        print("tables:", tables)
