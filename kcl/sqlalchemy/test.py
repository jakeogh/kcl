#!/usr/bin/env python3
from getdents import files
from kcl.printops import eprint
import os
from pkg_resources import resource_filename


def test(package, keep_databases, count, test_class=None, test_match=None):
    if test_class:
        test_path = resource_filename(package, 'test/tests/' + test_class)
    else:
        test_path = resource_filename(package, 'test/tests')
    if keep_databases:
        os.putenv("keep_test_databases", "True")
        #print(os.getenv("keep_test_databases"))
    eprint("test_path:", test_path)
    index = 0
    for test_file in files(test_path):
        if test_match:
            if test_match not in test_file:
                continue

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
