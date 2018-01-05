#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.database.tables import tables
from kcl.sqlalchemy.clickapp.cli.database.fields import fields
from kcl.sqlalchemy.clickapp.cli.database.print_database import print_database

@click.group()
def database():
    pass

database.add_command(tables)
database.add_command(fields)
database.add_command(print_database, name="print")
