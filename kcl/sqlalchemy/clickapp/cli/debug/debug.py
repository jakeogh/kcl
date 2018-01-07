#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.ipython import ipython
from kcl.sqlalchemy.clickapp.cli.debug.database.database import database

@click.group()
def debug():
    pass

debug.add_command(ipython)
debug.add_command(database)
