#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from kcl.printops import eprint
from kcl.sqlalchemy.create_session import create_session

def delete_and_recreate_database(database):
    try:
        delete_database(database=database)
    except ProgrammingError:
            pass #db didnt exist
    finally:
        create_database(database=database)

