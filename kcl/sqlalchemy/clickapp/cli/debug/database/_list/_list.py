#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.database._list._class import _class
from kcl.sqlalchemy.clickapp.cli.debug.database._list._fields import _fields

@click.group()
def _list():
    pass

_list.add_command(_class, name="class")
_list.add_command(_fields, name="fields")
