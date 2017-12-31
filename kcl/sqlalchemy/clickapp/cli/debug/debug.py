#!/usr/bin/env python3

import click
from kcl.sqlalchemy.clickapp.cli.debug.ipython import ipython

@click.group()
def debug():
    pass

debug.add_command(ipython)
