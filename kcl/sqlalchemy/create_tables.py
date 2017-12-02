#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kcl.sqlalchemy.get_engine import get_engine

def create_tables(database, schema):
    temp_engine = get_engine(database, echo=False)
    schema.metadata.create_all(temp_engine)

