#!/usr/bin/env python3

import click
from kcl.printops import eprint
from kcl.sqlalchemy.clickapp.cli.debug.create.record import record

@click.group()
def create():
    pass

create.add_command(record, name='record')
