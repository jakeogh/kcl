#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from kcl.sqlalchemy.BaseMixin import BASE

class PathRecord(BASE):
    '''
    Path instances are composed of a PathRecord instance.

    Each PathRecord maps a Filename to a position and a specific Path.
    position is always 0 unless the path is composed of multiple PathRecord instances
    The Slide/Bullett example:
        http://docs.sqlalchemy.org/en/latest/orm/extensions/orderinglist.html
        seems to confirm that PathRecords are necessary because in this instance
        many Slides(Paths) can have the same Bullet(Filename), and in the example
        a Bullet can only exist on one Slide.

    The pathfilename table has a row count:
    of (4 col) that are parsed by the ORM to reconstruct each Path's __repr__.
    * row_count = count of every filename in every path including duplicates
    * row_count = paths + spaces
    Does not appear to be a big deal because it's not exp and most paths have 0 spaces

    '''
    __table_args__ = (UniqueConstraint('path_id', 'filename_id'),)
    id = Column(Integer, primary_key=True, unique=True)

    path_id = Column(Integer,
                     ForeignKey("path.id"),
                     unique=False,
                     primary_key=False)
    #path = relationship("Path", backref='basepath')

    filename_id = Column(Integer,
                         ForeignKey("filename.id"),
                         unique=False,
                         primary_key=False)
    filename = relationship("Filename", backref='pathrecords')


    @classmethod
    def construct(cls, *, session, path, **kwargs):
        base_path = os.path.dirname(path)
        if base_path == b'/':
            ceprint("found /")
        filename = path.split(b'/')[-1]



    ## Must be signed int because -1 has special meaning
    ##position_constraint = 'position<100' # limit filenames/path to 100
    ##position = Column(Integer, CheckConstraint(position_constraint), unique=False, primary_key=True)
    #position = Column(Integer, unique=False, primary_key=True)
    #previous_position_constraint = \
    #    '(previous_position IS NULL AND position = 0) ' + \
    #    'OR ((previous_position = position - 1) IS TRUE)'

    ## primary_key=False because it can be Null
    #previous_position = Column(Integer,
    #                           CheckConstraint(previous_position_constraint),
    #                           primary_key=False,
    #                           nullable=True)
    # collection_class=set?

    def __repr__(self):
        return 'PathRecord<' + \
            'filename: ' + str(self.filename) + \
            ', path_id: ' + str(self.path_id) + \
            ', filename_id: ' + str(self.filename_id) + '>'
        #return 'PathRecord<' + \
        #    'filename: ' + str(self.filename) + \
        #    ', path_id: ' + str(self.path_id) + \
        #    ', filename_id: ' + str(self.filename_id) + \
        #    ', position: ' + str(self.position) + \
        #    ', previous_position: ' + str(self.previous_position) + '>'

