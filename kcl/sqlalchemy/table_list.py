#!/usr/bin/env python3

from pprint import pprint
from sqlalchemy.exc import ProgrammingError
from kcl.sqlalchemy.model.BaseMixin import BASE
from kcl.sqlalchemy.self_contained_session import self_contained_session

def table_list(database, verbose=False, contents=False, table=False):
    with self_contained_session(database) as session:
        engine = session.bind
        BASE.metadata.reflect(engine)
        table_names = BASE.metadata.tables.keys()
        table_list = []
        only_table = table
        for table in table_names:
            if only_table:
                if table != only_table:
                    continue
            table_instance = BASE.metadata.tables[table]
            if verbose:
                pprint(table_instance)
            #else:
            #    print(table)
            if contents:
                try:
                    pprint(session.query(table_instance).all())
                    print('')
                except ProgrammingError:
                    session.rollback()
            table_list.append(table)
        return table_list
