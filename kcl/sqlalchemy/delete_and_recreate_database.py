#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kcl.printops import eprint

def delete_and_recreate_database(database):
    try:
        delete_database(database=database)
    except ProgrammingError:
            pass #db didnt exist
    finally:
        create_database(database=database)

