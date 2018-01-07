#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
'''
Filename class
'''

from sqlalchemy import Column
#from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
#from sqlalchemy import LargeBinary  # bytea on postgresql
from sqlalchemy.dialects.postgresql import BYTEA
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.sqlalchemy.BaseMixin import BASE

# https://www.postgresql.org/docs/current/static/datatype-binary.html
# https://www.postgresql.org/docs/current/static/functions-binarystring.html
# https://stackoverflow.com/questions/6637843/query-bytea-field-in-postgres-via-command-line
# https://dba.stackexchange.com/questions/130812/query-bytea-column-using-prefix
# https://www.postgresql.org/message-id/1657180000.1070472048%40gnarzelwicht.delirium-arts.de


class Filename(BASE):
    '''
    UNIX filenames can be anything but NULL and / therefore a binary type is required.
    max file name length is 255 on all UNIX-like filesystems
    this does not store the path to the filename, so / is not allowed
    '''
    id = Column(Integer, primary_key=True)

    filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0" #todo test
    #filename = Column(LargeBinary(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)
    filename = Column(BYTEA(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)

    @classmethod
    def construct(cls, session, filename):
        #print("Filename.construct()")
        assert filename #hm..
        result = get_one_or_create(session, Filename, filename=filename)
        return result

    def __repr__(self):
        return "<Filename(filename=%s)>" % (str(self.filename))

    #def __repr__(self):
    #    return str(self.filename)

    def __bytes__(self):
        return self.filename
