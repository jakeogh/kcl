#!/usr/bin/env python3
import click
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.self_contained_session import self_contained_session

@click.command()
@click.pass_obj
def ipython(config):
     with self_contained_session(config.database, echo=CONFIG.database_echo) as session:
        print("CONFIG.database_echo:", CONFIG.database_echo)
        BASE.metadata.create_all(session.bind)
        import IPython; IPython.embed()
