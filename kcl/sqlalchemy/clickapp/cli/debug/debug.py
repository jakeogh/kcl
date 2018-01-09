#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.ipython import ipython
from kcl.sqlalchemy.clickapp.cli.debug.database.database import database
from kcl.sqlalchemy.clickapp.cli.debug.config import config
from kcl.sqlalchemy.clickapp.cli.debug._create._create import _create


@click.group()
def debug():
    pass


debug.add_command(ipython)
debug.add_command(database)
debug.add_command(config)
debug.add_command(_create, name="create")
