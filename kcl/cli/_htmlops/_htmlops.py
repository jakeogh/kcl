#!/usr/bin/env python3

import click
from kcl.cli._htmlops._lxml import _lxml
#from kcl.cli._htmlops._text import _text


@click.group()
def _create():
    pass


_create.add_command(_lxml, name='lxml')
#_create.add_command(_text, name='text')
