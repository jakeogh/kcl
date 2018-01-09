#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.database.tables import tables
from kcl.sqlalchemy.clickapp.cli.debug.database.fields import fields
from kcl.sqlalchemy.clickapp.cli.debug.database.print_database import print_database
from kcl.sqlalchemy.clickapp.cli.debug._count._count import _count
from kcl.sqlalchemy.clickapp.cli.debug._list._list import _list

@click.group()
def database():
    pass

database.add_command(tables)
database.add_command(fields)
database.add_command(print_database, name="print")
database.add_command(_list, name="list")
database.add_command(_count, name="count")
