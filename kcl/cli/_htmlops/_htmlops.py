#!/usr/bin/env python3

import click
from kcl.cli._htmlops._lxml import _lxml
from kcl.cli._htmlops._text import _text


@click.group()
def _htmlops():
    pass


_htmlops.add_command(_lxml, name='lxml')
_htmlops.add_command(_text, name='text')
