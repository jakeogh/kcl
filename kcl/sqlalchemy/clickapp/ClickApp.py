#!/usr/bin/env python3

import click
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database
from kcl.printops import eprint
from kcl.sqlalchemy.test import test as kcltest
from kcl.sqlalchemy.print_database import print_database as kcl_print_database
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.ipython import ipython
#from fsindex.model.Config import CONFIG
from kcl.click.CONTEXT_SETTINGS import CONTEXT_SETTINGS
#from .cli.list_objects.list_objects import list_objects
#from .cli.create_objects.create_objects import create_objects
#from .cli.visualization.sa_display import sa_display

__version__ = 0.01



class ClickApp():
    def __init__(self, config):
        self.config = config

    def add_doc(self, value):
        def _doc(func):
            func.__doc__ = "test"
            return func
        return _doc

    # pylint: disable=C0326
    # http://pylint-messages.wikidot.com/messages:c0326
    @click.group(context_settings=CONTEXT_SETTINGS)
    #@click.option('--verbose', is_flag=True, callback=set_verbose, expose_value=True)
    @click.option('--verbose', is_flag=True)
    @click.option('--database', is_flag=False, type=str, required=False)
    @click.option('--temp-database', is_flag=True, required=False)
    @click.option('--delete-database', is_flag=True, required=False)
    @click.pass_context
    @add_doc
    def clickapp(self, ctx, verbose, database, temp_database, delete_database):
        #__doc__ = self.config.appname + "orm interface"
        #self.__doc__ = self.config.appname + "orm interface"
        #''' clickapp orm interface'''
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

#@clickapp.command()
#@click.option('--package', is_flag=False, type=str, required=False, default='clickapp')
#@click.option('--keep-databases', is_flag=True)
#@click.option('--count', is_flag=False, type=int, required=False)
#@click.option('--test-class', is_flag=False, type=str, required=False)
#@click.option('--test-match', is_flag=False, type=str, required=False)
#def test(package, keep_databases, count, test_class, test_match):
#    kcltest(package=package, keep_databases=keep_databases, count=count, test_class=test_class, test_match=test_match)
#
#
##@click.pass_obj
#@clickapp.command()
#@click.option('--table', type=str, default=False)
#@click.pass_context
#def print_database(ctx, table):
#    ctx.invoke(kcl_print_database, database=ctx.obj.database, table=table)
#
#
##clickapp.add_command(list_objects, name='list')
##clickapp.add_command(create_objects, name='create')
##clickapp.add_command(print_database)
#clickapp.add_command(ipython)
##clickapp.add_command(sa_display)
#
##clickapp.add_command(bookmark)
##clickapp.add_command(show_config, name='config')
##clickapp.add_command(display_database)
##clickapp.add_command(import_all_iris)
