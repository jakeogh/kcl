#!/usr/bin/env python3

import click
from kcl.cli._dirops._iterate import _iterate


@click.group()
def _dirops():
    pass


_dirops.add_command(_iterate, name='iterate')
