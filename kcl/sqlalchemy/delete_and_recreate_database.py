#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kcl.printops import eprint
from kcl.sqlalchemy.delete_database import delete_database
from sqlalchemy_utils.functions import create_database
from sqlalchemy.exc import ProgrammingError


def delete_and_recreate_database(database):
    #delete_database(database)
    #create_database(database)

    try:
        delete_database(database)
    except ProgrammingError:
            pass  # db didnt exist
    finally:
        create_database(database)

