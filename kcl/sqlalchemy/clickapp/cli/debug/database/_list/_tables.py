#!/usr/bin/env python3

import click
from kcl.sqlalchemy.table_list import table_list as sqla_list_tables
from kcl.sqlalchemy.self_contained_session import self_contained_session

@click.command()
@click.option('--table', default=None)
@click.option('--contents', is_flag=True)
@click.pass_obj
def _tables(config, table, contents):
#   with self_contained_session(config.database) as session:
    sqla_list_tables(database=config.database, contents=contents, table=table)

