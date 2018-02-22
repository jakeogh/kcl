#!/usr/bin/env python3

import builtins
CONFIG = builtins.config

import click
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database
from kcl.printops import eprint
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.model.BaseMixin import BASE
from kcl.click.CONTEXT_SETTINGS import CONTEXT_SETTINGS

__version__ = 0.01


@click.group(context_settings=CONTEXT_SETTINGS, help="boilerplate orm interface")
@click.option('--verbose', is_flag=True)
@click.option('--database', is_flag=False, type=str, required=False)
@click.option('--temp-database', is_flag=True, required=False)
@click.option('--delete-database', is_flag=True, required=False)
@click.option('--debug', is_flag=True, required=False)
@click.pass_context
def clickapp(ctx, verbose, database, temp_database, delete_database, debug):
    if database:
        if temp_database:
            eprint("Error: --database and --temp-database are mutually exclusive.")
            quit(1)
        CONFIG.database = database
    elif temp_database:
        CONFIG.database = CONFIG.database_timestamp
    else:
        CONFIG.database = CONFIG.database_real(CONFIG.appname)
    if delete_database:
        if database_exists(CONFIG.database):
            drop_database(CONFIG.database)
    if not database_exists(CONFIG.database):
        create_database(CONFIG.database)
        with self_contained_session(CONFIG.database) as session:
            BASE.metadata.create_all(session.bind)
    if verbose:
        eprint(CONFIG.database)
        CONFIG.database_echo = True
    ctx.obj = CONFIG
    if debug:
        from pudb import set_trace; set_trace(paused=True)
