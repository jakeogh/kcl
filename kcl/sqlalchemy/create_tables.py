#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

def create_tables(database, schema):
    temp_engine = create_engine(database, echo=False)
    schema.metadata.create_all(temp_engine)

