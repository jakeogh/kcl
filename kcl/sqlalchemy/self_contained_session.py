#!/usr/bin/env python3

import contextlib
import os

#import psycopg2  # import OperationalError
from icecream import ic
#: (psycopg2.OperationalError) could not connect to server: Connection refused
from kcl.serviceops import get_latest_postgresql_version
from retry_on_exception import retry_on_exception
from sqlalchemy_utils.functions import create_database, database_exists

from sqlalchemy import create_engine
#from kcl.printops import eprint
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool


def start_database(verbose=False):
    latest = get_latest_postgresql_version(verbose=False)
    command = "/etc/init.d/postgresql-{} start".format(latest)
    if verbose:
        ic(command)
    os.system(command)


@retry_on_exception(exception=OperationalError,
                    in_e_args="could not connect to server: Connection refused",
                    max_delay=1,
                    call_function_once=start_database,
                    call_function_once_kwargs={'verbose':True},
                    debug=True,
                    verbose=True,)
def database_already_exists(db_url):
    return database_exists(db_url)


# https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
@contextlib.contextmanager
def self_contained_session(db_url, echo=False, engine=False, verbose=False):
    if verbose:
        ic(db_url)

    if not database_already_exists(db_url):  # executes SELECT 1 FROM pg_database WHERE datname='path_test_1520320264'
        print("creating empty database:", db_url)
        create_database(db_url)  # executes CREATE DATABASE

    if not engine:
        engine = create_engine(db_url, poolclass=NullPool, echo=echo)
    connection = engine.connect() # executes query
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_session
    # db_session.close() # pylint says: Instance of 'scoped_session' has no 'close' member (no-member)
    # further reading the docs, since db_session is a scoped_session:
    # http://docs.sqlalchemy.org/en/latest/orm/contextual.html
    # The scoped_session.remove() method first calls Session.close() on the current Session,
    # which has the effect of releasing any connection/transactional resources owned by the
    # Session first, then discarding the Session itself. “Releasing” here means that
    # connections are returned to their connection pool and any transactional state is rolled
    # back, ultimately using the rollback() method of the underlying DBAPI connection.
    #
    # so in short, even though its not throwing a runtime error, dont db_session.close()
    # instead call db_session.remove() if using scoped_session
    db_session.remove() # should call Session.close() on its own
    connection.close()
    engine.dispose() # not sure how necessary this is
