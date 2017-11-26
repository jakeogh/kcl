#!/usr/bin/env python3

import click
from kcl.dirops import all_files
from kcl.printops import eprint
import os
import pkg_resources

TEST_PATH = pkg_resources.resource_filename('iridb', 'test/tests')

@click.command()
@click.option('--keep-databases', is_flag=True)
@click.option('--count', is_flag=False, type=int, required=False)
def test(keep_databases, count):
    if keep_databases:
        os.putenv("iridb_keep_test_databases", "True")
        print(os.getenv("iridb_keep_test_databases"))
    eprint("TEST_PATH:", TEST_PATH)
    os.system('sudo /home/cfg/database/postgresql/start')
    index = 0
    for test_file in all_files(TEST_PATH):

        if test_file.endswith('''.py''') and not test_file.endswith('__init__.py'):
            index += 1
            if count:
                if index > count:
                    break
            print("\nrunning test:", test_file)
            exit_status = os.WEXITSTATUS(os.system(test_file))
            if exit_status != 0:
                quit(exit_status)

    print("\n\nAll Tests Completed OK")
