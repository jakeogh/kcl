#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.ipython import ipython
from kcl.sqlalchemy.clickapp.cli.debug.start_pudb import start_pudb

@click.group()
def debug():
    pass

debug.add_command(ipython)
debug.add_command(start_pudb, name='pudb')
