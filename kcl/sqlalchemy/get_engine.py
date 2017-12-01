#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

def get_engine_broken(database):
    assert isinstance(database, str)
    engine = create_engine(database, echo=False)
    return engine
