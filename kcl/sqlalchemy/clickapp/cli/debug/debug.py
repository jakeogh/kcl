#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.ipython import ipython
from kcl.sqlalchemy.clickapp.cli.debug.database.database import database
from kcl.sqlalchemy.clickapp.cli.debug.config import config

@click.group()
def debug():
    pass

debug.add_command(ipython)
debug.add_command(database)
debug.add_command(config)
