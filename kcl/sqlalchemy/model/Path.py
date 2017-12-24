#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
'''
Path class
'''
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
from sqlalchemy import LargeBinary # bytea on postgresql
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.sqlalchemy.BaseMixin import BASE

class Path(BASE):
    '''
    UNIX paths can be anything but NULL
    max path length is undefined:
        http://insanecoding.blogspot.com/2007/11/pathmax-simply-isnt.html
    all paths must start and end with /
    '''
    id = Column(Integer, primary_key=True)
    #path_constraint = "position('\\x00' in path) = 0 and position('\\x2f' in path) = 0"
    path_constraint = "position('\\x00' in path) = 0" #todo test, add constraint to replace asserts
    path = Column(LargeBinary(), CheckConstraint(path_constraint), unique=True, nullable=False, index=True)

    @classmethod
    def construct(cls, session, path):
        assert isinstance(path, bytes)
        assert path.startswith(b'/')
        #assert path.endswith(b'/')
        #print("Path.construct()")
        result = get_one_or_create(session, Path, path=path)
        return result

    def __repr__(self):
        return str(self.path)    #todo: going to fail if it's outside Unicode
