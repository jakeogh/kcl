#!/usr/bin/env python3

import click
from kcl.cli._dbops._visualize import _print_database


@click.group()
def _dbops():
    pass


_dirops.add_command(_print_database, name='print-database')
