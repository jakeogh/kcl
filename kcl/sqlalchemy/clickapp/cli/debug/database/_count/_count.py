#!/usr/bin/env python3

import click
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.table_list import table_list as sqla_list_tables
from kcl.click.CONTEXT_SETTINGS import CONTEXT_SETTINGS
CONTEXT_SETTINGS['ignore_unknown_options'] = True
CONTEXT_SETTINGS['allow_extra_args'] = True


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--table', type=str, default=None, required=False)
@click.pass_context
def _count(ctx, table):
    with self_contained_session(ctx.obj.database) as session:
        if table:
            tables = [table]
        else:
            tables = sqla_list_tables(database=ctx.obj.database, contents=False, table=None)
        for table in sorted(tables):
            constructed_test = 'select COUNT(*) from %s;' % table
            answer = session.execute(constructed_test)
            for result in answer:
                if len(tables) == 1:
                    print(result[0])
                else:
                    print(table, result[0])
