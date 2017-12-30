#!/usr/bin/env python3

import click
import builtins
CONFIG = builtins.config
from kcl.sqlalchemy.test import test as kcltest

@click.command()
@click.option('--keep-databases', is_flag=True)
@click.option('--count', is_flag=False, type=int, required=False)
@click.option('--test-class', is_flag=False, type=str, required=False)
@click.option('--test-match', is_flag=False, type=str, required=False)
def test(keep_databases, count, test_class, test_match):
    package = CONFIG.appname
    kcltest(package=package, keep_databases=keep_databases, count=count, test_class=test_class, test_match=test_match)

