#!/usr/bin/env python3
from kcl.postgresqlops import create_session
from kcl.sqlalchemy.BaseMixin import BASE
from pprint import pprint
import click
from sqlalchemy.exc import ProgrammingError

@click.command()
@click.argument("database", nargs=1)
@click.option("--verbose", is_flag=True)
@click.option("--contents", is_flag=True)
def list_tables(database, verbose, contents):
    session = create_session(database=database)
    engine = session.bind
    BASE.metadata.reflect(engine)
    table_names = BASE.metadata.tables.keys()
    for table in table_names:
        print(" ")
        table_instance = BASE.metadata.tables[table]
        if verbose:
            pprint(table_instance)
        else:
            print(table)
        if contents:
            try:
                pprint(session.query(table_instance).all())
            except ProgrammingError:
                session.rollback()
