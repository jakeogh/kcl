#!/usr/bin/env python3

import click
import builtins
CONFIG = builtins.config

import pprint
from kcl.printops import eprint
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.table_list import table_list
from sqlalchemy.sql import text

#from kcl.sqlalchemy.visualization.print_database import print_database as kcl_print_database

def match_field(session, table, field, term, substring):
    tables = table_list(database=session.bind.url)
    if table not in tables: # todo make decorator
        eprint("non existing table:", table, "valid tables:", tables)
        quit(1)

    if substring:
        query = '''SELECT * FROM ''' + table + ''' WHERE ''' + field + ''' LIKE :term'''
        query = text(query)
        term = '%'+term+'%'
    else:
        query = '''SELECT * FROM ''' + table + ''' WHERE ''' + field + ''' = :term'''
        query = text(query)

    query = query.bindparams(term=term)
    answer = session.execute(query)
    results = answer.fetchall()
    return results


@click.command()
#@click.option('--field', required=True, nargs=1, type=click.Choice(list(FIELDS.keys())))
@click.option('--table', required=True, nargs=1)
@click.option('--field', required=True, nargs=1)
@click.option('--term', required=True, nargs=1)
@click.option('--substring', is_flag=True)
@click.pass_obj
def _search(config, table, field, term, substring):
    eprint(field, term, substring)
    with self_contained_session(config.database, echo=config.database_echo) as session:
        results = match_field(session=session, table=table, field=field, term=term, substring=substring)
        for result in results:
            pprint.pprint(result)
            #yield result



#@click.command()
#@click.option('--table', type=str, default=False)
#@click.pass_context
#def _print(ctx, table):
#    ctx.invoke(kcl_print_database, database=CONFIG.database, table=table, contents=True)
