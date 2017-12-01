#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from kcl.printops import eprint

def create_session(database, multithread=False):
    eprint("creating session for:", database)
    if not multithread:
        engine = create_engine(database, echo=False, poolclass=NullPool)
        session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    else:
        engine = create_engine(database, echo=False, pool_size=20, max_overflow=100)
        session = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
    return session
