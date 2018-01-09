#!/usr/bin/env python3

import click
from kcl.sqlalchemy.self_contained_session import self_contained_session
#from kcl.sqlalchemy.BaseMixin import BASE
from kcl.click.CONTEXT_SETTINGS import CONTEXT_SETTINGS
CONTEXT_SETTINGS['ignore_unknown_options'] = True
CONTEXT_SETTINGS['allow_extra_args'] = True


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('table_name', type=str, nargs=1)
@click.pass_context
def _count(ctx, table_name):
    with self_contained_session(ctx.obj.database) as session:
        constructed_test = 'select COUNT(*) from %s;' % table_name
        answer = session.execute(constructed_test)
        for result in answer:
            print(result)
