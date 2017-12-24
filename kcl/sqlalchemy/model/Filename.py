#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
'''
Filename class
'''

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
from sqlalchemy import LargeBinary # bytea on postgresql
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.sqlalchemy.BaseMixin import BASE

class Filename(BASE):
    '''
    UNIX filenames can be anything but NULL and / therefore a binary type is required.
    max file name length is 255 on all UNIX-like filesystems
    this does not store the path path to the filename, so / is not allowed
    '''
    id = Column(Integer, primary_key=True)

    #filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0"
    filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0" #todo test
    filename = Column(LargeBinary(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)

    @classmethod
    def construct(cls, session, filename):
        #print("Filename.construct()")
        result = get_one_or_create(session, Filename, filename=filename)
        return result

    def __repr__(self):
        return str(self.filename)
    def __bytes__(self):
        return self.filename
