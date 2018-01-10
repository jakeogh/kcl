#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.database._list._class import _class
from kcl.sqlalchemy.clickapp.cli.debug.database._list._fields import _fields

@click.group()
def _list():
    pass

database.add_command(_class, name="class")
database.add_command(_fields, name="fields")
