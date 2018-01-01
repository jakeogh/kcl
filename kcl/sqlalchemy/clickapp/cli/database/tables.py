#!/usr/bin/env python3

import click
from kcl.sqlalchemy.list_tables import list_tables as sqla_list_tables
from kcl.sqlalchemy.self_contained_session import self_contained_session

@click.command()
@click.option('--contents', is_flag=True)
@click.pass_obj
def tables(config, contents):
    with self_contained_session(config.database) as session:
        sqla_list_tables(database=config.database, contents=contents)

