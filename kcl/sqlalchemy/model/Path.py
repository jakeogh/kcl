#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

'''
Implements Paths (Filenames seperated by "/").

Paths are a sequence of Filenames separated by "/".
Path examples:
    "/plants"
    "trees"
    "Eucalyptus/deglupta"
    "/867-5309"
    "/☃/Snowman!"

Paths are composed of 1 or more ordered Filenames.
All Filenames for the Path list above:
    "plants"
    "trees"
    "Eucalyptus"
    "deglupta"
    "867-5309"
    "☃"
    "Snowman!"

Filenames are unique.

Paths are composed of Filenames in a specific order, that order is defined by class PathFilename
Each PathFilename instance maps a Filename to a position.
So, actually, Path.filenames is a list of PathFilename instances, not Filename instances.
'''

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from kcl.sqlalchemy.BaseMixin import BASE
from .Filename import Filename
from .PathFilename import PathFilename
from .find_path import find_path


class Path(BASE):
    id = Column(Integer, primary_key=True)
    pathfilenames = relationship("PathFilename", backref='path')

    def __init__(self, session, path):
        assert isinstance(path, bytes)
        assert not find_path(session=session, path=path) # because get_one_or_create should have already found it
        for index, filename in enumerate(path.split(b'/')):
            previous_position = index - 1
            if previous_position == -1:
                previous_position = None
            pathfilename = PathFilename(position=index, previous_position=previous_position)
            pathfilename.filename = Filename.construct(session=session, filename=filename)
            self.pathfilenames.append(pathfilename)
        session.add(self)
        session.flush(objects=[self])


    @classmethod
    def construct(cls, *, session, path, **kwargs):
        '''
        prevents creation of duplicate paths
        prevents creation of a path that conflicts with an existing alias
        '''
        assert path
        if isinstance(path, str):
            path = bytes(path, encoding='UTF8') # handle command line input

        existing_path = find_path(session=session, path=path)
        if existing_path:
            return existing_path
        ceprint("new_path:", path)
        new_path = cls(path=path, session=session)
        return new_path

    @property
    def path(self):  # appears to always return the same result as path_with_checks()
        path = b'/'.join([filename.filename for filename in self.filenames])
        return path

    @hybrid_property
    def filenames(self):
        filename_list = []
        for pathfilename in self.pathfilenames:
            # path_filename = getattr(filename, self.pathfilename)
            filename_list.append(pathfilename.filename)
        return filename_list  # cant be a set because "a a" -> "a"


    def __repr__(self):
        return "<Path(path=%s)>" % (str(self.path))

    def __bytes__(self):
        return self.path




#class PathClassConstructor():
#    def __new__(cls, mapper_to_bookmark):
#        class_attr = {}
#        class_attr['id'] = Column(Integer, primary_key=True)
#        class_attr['pathfilenames'] = relationship("PathFilename", backref='path') # list of PathFilename instances
#        target_class_name = mapper_to_bookmark.__name__
#        target_name = target_class_name.lower().split('.')[-1]  # 'filename' usually
#
#        class_attr['target_class_name'] = target_class_name
#        class_attr['target_name'] = target_name
#
#        class_attr['__init__'] = init
#        class_attr['__repr__'] = display
#        class_attr['construct'] = construct         # @classmethod
#        class_attr['path'] = build_path               # @property
#        class_attr[target_name+'s'] = path_targets   # @hybrid_property
#        class_attr['filenames'] = filenames                 # @hybrid_property
#        return type('Path', (BASE,), class_attr)
#
#
#def init(self, session, path):
#    assert isinstance(path, str)
#    assert not find_path(session=session, path=path) # because get_one_or_create should have already found it
#    for index, filename in enumerate(path.split(' ')):
#        previous_position = index - 1
#        if previous_position == -1:
#            previous_position = None
#        pathfilename = PathFilename(position=index, previous_position=previous_position)
#        pathfilename.filename = Filename.construct(session=session, filename=filename)
#        self.pathfilenames.append(pathfilename)
#    session.add(self)
#    session.flush(objects=[self])
#
#def display(self):
#    return str(self.path)
#
#@classmethod
#def construct(cls, session, path, **kwargs):
#    '''
#    prevents creation of duplicate paths
#    prevents creation of a path that conflicts with an existing alias
#    '''
#    assert path
#    existing_alias = find_alias(session=session, alias=path)
#    if existing_alias:
#        return existing_alias.path
#    existing_path = find_path(session=session, path=path)
#    if existing_path:
#        return existing_path
#    new_path = cls(path=path, session=session)
#    return new_path
#
#@property
#def build_path(self): # appears to always return the same result as path_with_checks()
#    path = " ".join([str(filename) for filename in self.filenames])
#    return path
#
#@hybrid_property
#def path_targets(self):
#    target_list = []
#    for bookmark in self.bookmarks:
#        target = getattr(bookmark, self.target_name)
#        target_list.append(target)
#    return set(target_list)
#
#@hybrid_property
#def filenames(self):
#    filename_list = []
#    for pathfilename in self.pathfilenames:
#        # path_filename = getattr(filename, self.pathfilename)
#        filename_list.append(pathfilename.filename)
#    return filename_list # cant be a set because "a a" -> "a"
#
### not sure if sorting is necessary
##    @property
##    def path_with_checks(self):
##        pathfilenames_objects = sorted([filename for filename in self.filenames], key=lambda x: x.position)
##        sorted_path = " ".join([str(filename.filename) for filename in pathfilenames_objects])
##
##        unsorted_path = " ".join([filename.filename for filename in self.filenames])
##        if sorted_path != unsorted_path:
##            print("TAGS DO NOT MATCH")
##            print("sorted_path:", sorted_path)
##            print("unsorted_path:", unsorted_path)
##            quit(1)
##        return unsorted_path

