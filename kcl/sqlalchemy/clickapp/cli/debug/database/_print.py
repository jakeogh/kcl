#!/usr/bin/env python3

import click
import builtins
CONFIG = builtins.config
from kcl.sqlalchemy.visualization.print_database import print_database as kcl_print_database

@click.command()
@click.option('--table', type=str, default=False)
@click.pass_context
def _print(ctx, table):
    ctx.invoke(kcl_print_database, database=CONFIG.database, table=table, contents=True)
