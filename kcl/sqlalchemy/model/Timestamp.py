#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

'''
 Timestamp with timezone
'''
import os
import decimal
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.sqlalchemy.BaseMixin import BASE

# https://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/models.html#Timestamp

class Timestamp(BASE):
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), unique=True, nullable=False, index=True, server_default=func.now())

    #@classmethod
    #def construct(cls, session):
    #    result = getattr(Timestamp, )
    #    result = get_one_or_create(session, Timestamp)
    #    return result

    def __repr__(self):
        return str(self.timestamp)
