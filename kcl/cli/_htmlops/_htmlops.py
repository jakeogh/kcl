#!/usr/bin/env python3

import click
from kcl.cli._htmlops._lxml import _lxml
from kcl.cli._htmlops._text import _text
from kcl.cli._htmlops._html import _html


@click.group()
def _htmlops():
    pass


_htmlops.add_command(_lxml, name='lxml')
_htmlops.add_command(_text, name='text')
_htmlops.add_command(_html, name='html')
