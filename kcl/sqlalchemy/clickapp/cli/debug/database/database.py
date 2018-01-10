#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.database._list._list import _list
from kcl.sqlalchemy.clickapp.cli.debug.database._list._tables import _tables
from kcl.sqlalchemy.clickapp.cli.debug.database._list._fields import _fields
from kcl.sqlalchemy.clickapp.cli.debug.database._count._count import _count
from kcl.sqlalchemy.clickapp.cli.debug.database._create._create import _create
from kcl.sqlalchemy.clickapp.cli.debug.database._print import _print

@click.group()
def database():
    pass

database.add_command(tables)
database.add_command(fields)
database.add_command(_print, name="print")
database.add_command(_list, name="list")
database.add_command(_create, name="create")
database.add_command(_count, name="count")
