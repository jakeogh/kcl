#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.database._list._list import _list
from kcl.sqlalchemy.clickapp.cli.debug.database._count._count import _count
from kcl.sqlalchemy.clickapp.cli.debug.database._create._create import _create
from kcl.sqlalchemy.clickapp.cli.debug.database._print import _print
from kcl.sqlalchemy.clickapp.cli.debug.database._search import _search

@click.group()
def database():
    pass

database.add_command(_print, name="print")
database.add_command(_search, name="search")
database.add_command(_list, name="list")
database.add_command(_create, name="create")
database.add_command(_count, name="count")
