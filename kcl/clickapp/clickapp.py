#!/usr/bin/env python3

import builtins
CONFIG = builtins.config

import click
from kcl.printops import eprint
from kcl.printops import ceprint
from kcl.cli.CONTEXT_SETTINGS import CONTEXT_SETTINGS

__version__ = 0.01


@click.group(context_settings=CONTEXT_SETTINGS, help="boilerplate click interface")
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True, required=False)
@click.pass_context
def clickapp(ctx, verbose, debug):
    #ceprint("entered clickapp()")
    ctx.obj = CONFIG
    if debug:
        from pudb import set_trace; set_trace(paused=True)
