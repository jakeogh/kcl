#!/usr/bin/env python3

import click
from kcl.cli._redisops._keys import _keys


@click.group()
def _redisops():
    pass


_redisops.add_command(_keys, name='keys')
