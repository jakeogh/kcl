#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import CheckConstraint
from kcl.sqlalchemy.model.BaseMixin import BASE

path_constraint = 'path_id!=path_parent_id'

path_relationship = Table(
    'path_relationship', BASE.metadata,
    Column('path_parent_id', Integer, ForeignKey('path.id')),
    Column('path_id', Integer, ForeignKey('path.id')),
    CheckConstraint(path_constraint))
