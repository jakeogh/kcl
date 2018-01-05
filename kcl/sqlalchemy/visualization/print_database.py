#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

import pprint
import click
from sqlalchemy import inspect as sqlalchemy_inspect
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.printops import eprint

@click.command()
@click.argument('database')
@click.option('--table', type=str, default=False)
@click.option('--contents', is_flag=True)
def print_database(database, table, contents):
    with self_contained_session(database) as session:
        inspector = sqlalchemy_inspect(session.bind)
        table_list = sorted(inspector.get_table_names())
        if table:
            if table not in table_list:
                eprint("table: '%s' is not in table_list: %s" % (table, table_list))
                quit(1)
        for table_name in table_list:
            if table:
                if table_name != table:
                    continue
            else:
                print('\n' + table_name + ':')
            columns = inspector.get_columns(table_name)
            for column in columns:
                print("%s, " % column['name'], end='')
            print('\n', end='')
            if contents:
                select_statement = "select * from " + table_name + ";"
                pprint.pprint(session.execute(select_statement).fetchall())
