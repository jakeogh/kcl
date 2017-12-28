#!/usr/bin/env python3

import click
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database
from kcl.printops import eprint
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.ipython import ipython
from kcl.click.CONTEXT_SETTINGS import CONTEXT_SETTINGS

__version__ = 0.01

class ClickApp():
    def __init__(self, config):
        self.config = config

    @click.group(context_settings=CONTEXT_SETTINGS, help="boilerplate orm interface")
    @click.option('--verbose', is_flag=True)
    @click.option('--database', is_flag=False, type=str, required=False)
    @click.option('--temp-database', is_flag=True, required=False)
    @click.option('--delete-database', is_flag=True, required=False)
    @click.pass_context
    def clickapp(self, ctx, verbose, database, temp_database, delete_database):
        if database:
            if temp_database:
                eprint("Error: --database and --temp-database are mutually exclusive.")
                quit(1)
            self.config.database = database
        elif temp_database:
            self.config.database = self.config.database_timestamp
        else:
            self.config.database = self.config.database_real('clickapp')
        if delete_database:
            if database_exists(self.config.database):
                drop_database(self.config.database)
        if not database_exists(self.config.database):
            create_database(self.config.database)
            with self_contained_session(self.config.database) as session:
                BASE.metadata.create_all(session.bind)
        if verbose:
            eprint(self.config.database)
            self.config.database_echo = True
        ctx.obj = self.config

