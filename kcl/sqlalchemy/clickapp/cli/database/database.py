#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.database.tables import tables

@click.group()
def database():
    pass

debug.add_command(tables)
