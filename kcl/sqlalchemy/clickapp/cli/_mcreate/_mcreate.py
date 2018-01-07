#!/usr/bin/env python3

import click
from kcl.printops import eprint
from kcl.sqlalchemy.clickapp.cli._mcreate.record import record

@click.group()
def _mcreate():
    pass

_mcreate.add_command(record, name='record')
