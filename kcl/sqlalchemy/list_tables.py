#!/usr/bin/env python3
from kcl.postgresqlops import create_session
from kcl.sqlalchemy.BaseMixin import BASE
from pprint import pprint
import click

@click.command()
@click.argument("database", nargs=1)
@click.option("--verbose", is_flag=True)
def list_tables(database, verbose):
    session = create_session(database=database)
    engine = session.bind
    if verbose:
        BASE.metadata.reflect(engine)
        table_names = BASE.metadata.tables.keys()
        for table in table_names:
            print(" ")
            table_instance = BASE.metadata.tables[table]
            pprint(table_instance)
            pprint(session.query(table_instance).all())
    else:
        tables = engine.table_names()
        print("tables:", tables)
