#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from kcl.printops import eprint
from kcl.sqlalchemy.get_engine import get_engine
#from sqlalchemy.pool import QueuePool

def create_session_old(database, multithread=False):
    if not multithread:
        eprint("creating NullPool session for:", database)
        engine = get_engine(database, echo=False)
        session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    else:
        eprint("creating pool_size=20 session for:", database)
        engine = get_engine(database, echo=False, pool_size=20, max_overflow=100)
        session = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
    return session
