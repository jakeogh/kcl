#!/usr/bin/env python3

import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import database_exists

@contextlib.contextmanager # https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
def self_contained_session(db_url, echo=False):
    if not database_exists(db_url):
        create_database(db_url)
    engine = create_engine(db_url, poolclass=NullPool, echo=echo)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_session
    #db_session.close() # pylint says: Instance of 'scoped_session' has no 'close' member (no-member)
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
