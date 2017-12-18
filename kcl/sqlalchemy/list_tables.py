#!/usr/bin/env python3

from pprint import pprint
from sqlalchemy.exc import ProgrammingError
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.self_contained_session import self_contained_session

def list_tables(database, verbose=False, contents=False):
    with self_contained_session(database) as session:
        engine = session.bind
        BASE.metadata.reflect(engine)
        table_names = BASE.metadata.tables.keys()
        for table in table_names:
            print(" ")
            table_instance = BASE.metadata.tables[table]
            if verbose:
                pprint(table_instance)
            else:
                print(table)
            if contents:
                try:
                    pprint(session.query(table_instance).all())
                except ProgrammingError:
                    session.rollback()
