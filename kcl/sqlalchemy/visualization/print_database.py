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
        pad = len(max(table_list, key=len)) + 2
        if table:
            if table not in table_list:
                eprint("table: '%s' is not in table_list: %s" % (table, table_list))
                quit(1)
        for table_name in table_list:
            if table:
                if table_name != table:
                    continue
            else:
                padded_table_name = table_name + ':'
                print(padded_table_name.ljust(pad), end='')
            columns = inspector.get_columns(table_name)
            for column in columns:
                if table:
                    print(column['name'])
                else:
                    print("%s, " % column['name'], end='')
            if not table:
                print('\n', end='')
            if contents:
                select_statement = "select * from " + table_name + ";"
                data = session.execute(select_statement).fetchall()
                if data:
                    for result in data:
                        print(' '*pad, end='')
                        pprint.pprint(result)

if __name__ == '__main__':
    print_database()
