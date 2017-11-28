#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

import pprint
import click
from sqlalchemy import inspect as sqlalchemy_inspect
from kcl.sqlalchemy.create_session import create_session

@click.command()
@click.argument('database')
@click.option('--table', type=str, default=False)
def print_database(database, table):
    session = create_session(database=database)
    inspector = sqlalchemy_inspect(session.bind)
    for table_name in sorted(inspector.get_table_names()):
        if table:
            if table_name != table:
                continue
        print('\n' + table_name + ':')
        columns = inspector.get_columns(table_name)
        for column in columns:
            print("%s, " % column['name'], end='')
        print('\n', end='')
        select_statement = "select * from " + table_name + ";"
        pprint.pprint(session.execute(select_statement).fetchall())
