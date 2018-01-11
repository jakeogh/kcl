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

Paths are composed of Filenames in a specific order, that order is defined by class PathRecord
Each PathRecord instance maps a Filename to a position.
So, actually, Path.filenames is a list of PathRecord instances, not Filename instances.
'''

import os
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from kcl.printops import ceprint
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from .Filename import Filename
#from .PathRecord import PathRecord
from .find_path import find_path
from .path_relationship import path_relationship

class Path(BASE):
    id = Column(Integer, primary_key=True)

    parent = relationship('Path',
                          secondary=path_relationship,
                          primaryjoin=path_relationship.c.path_id == id,
                          secondaryjoin=path_relationship.c.path_parent_id == id,
                          backref="children")

    filename_id = Column(Integer,
                         ForeignKey("filename.id"),
                         unique=False,
                         primary_key=False)
    filename = relationship("Filename", backref='paths')

    #path = column_property(parent.filename + b'/' + filename)
    #path = column_property(b'/' + filename.filename)
    #path = column_property(filename)


    #def __init__(self, session, parent, path):
    #    assert isinstance(path, bytes)
    #    base_path = os.path.dirname(path)
    #    ceprint("base_path:", base_path)
    #    filename = path.split(base_path)[1]
    #    ceprint("filename:", filename)
    #    filename = get_one_or_create(session=session, Filename, filename=filename)
    #    if base_path == b'':
    #        #self.parent = None
    #        root_path = get_one_or_create(session=session, Path, parent=None, filename=filename)
    #        return root_path


    @classmethod
    def construct(cls, *, session, path, **kwargs):
        assert path
        ceprint("constructing path:", path)
        if isinstance(path, str):
            path = bytes(path, encoding='UTF8')  # handle command line input
        path_split = path.split(b'/')
        base_path = b'/'.join(path_split[0:-1])
        ceprint("base_path:", base_path)
        filename = path_split[-1]
        ceprint("filename:", filename)
        filename = get_one_or_create(session=session, model=Filename, filename=filename)
        if filename.filename == b'':
            ceprint("special case, empty filename for /")
            #new_path = get_one_or_create(session=session, model=Path, parent=None, filename=filename)
            root_path = get_one_or_create(session=session, model=Path, filename=filename)
            ceprint("returning root_path:", root_path.id)
            return root_path
        else:
            parent = get_one_or_create(session=session, model=Path, create_method='construct', create_method_kwargs={'path':base_path, 'session':session})
            #parent = cls.construct(session=session, path=base_path)

        new_path = get_one_or_create(session=session, model=Path, parent=parent, filename=filename)
        #new_path = cls(parent=parent, filename=filename)
        return new_path

        #path_split = path.split(b'/')
        #for index, element in reversed(path_split)
        #if path == b'/':
        #    ceprint("special case: /")
        #    filename = get_one_or_create(session=session, Filename, filename=b'')


        #existing_path = get_one_or_create(session=session, Path, path=path)
        #if existing_path:
        #    ceprint("found existing_path:", existing_path)
        #    return existing_path

        ##    ceprint("checking if it's a base path")
        ##    if existing_path.path != os.path.dirname(path):
        ##        ceprint("returning existing_path:", existing_path)
        ##        return existing_path
        ##    # at this point existing path has gotta be a base path
        ##    base_path = existing_path
        ##else:
        ##    ceprint("no existing path found, iterating over elements of path to make new base path")
        ##    path_split = path.split(b'/')
        ##    for index, filename in enumerate(path_split):
        ##        if index == 0: assert filename == b''

        ##    base_path = None

        ##end_filename = Filename.construct(session=session, filename=filename)
        ##new_pathrecord = PathRecord(base_path=base_path, filename=end_filename)


        ###ceprint("new_path:", path)
        ###new_path = cls(pathrecord=pathrecord, session=session)
        ##new_path = cls(pathrecord=pathrecord)
        ##return new_path

    #@property
    #def path(self):  # appears to always return the same result as path_with_checks()
    #    path = b'/'.join([pathrecord.path, pathrecord.filename])
    #    ceprint("path:", path)
    #    return path

    #@hybrid_property
    #def filenames(self):
    #    filename_list = []
    #    for pathfilename in self.pathfilenames:  # only one now
    #        # path_filename = getattr(filename, self.pathfilename)
    #        filename_list.append(pathfilename.path)
    #        filename_list.append(pathfilename.filename)
    #    return filename_list  # cant be a set because "a a" -> "a"


    #def __repr__(self):
    #    return "<Path(id=%s path=%s)>" % (str(self.id), str(self.path))

    #def __bytes__(self):
    #    return self.path




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

    #def __init__(self, session, pathrecord):
    #    assert isinstance(path, bytes)
    #    ##assert not find_path(session=session, path=path) # because get_one_or_create should have already found it
    #    #for index, filename in enumerate(path.split(b'/')):
    #    #    previous_position = index - 1
    #    #    if previous_position == -1:
    #    #        previous_position = None
    #    if not base_path:
    #        assert os.path.dirname(path) == b''
    #    else:
    #        assert len(path.split(base_path)[-1].split(b'/')) == 2
    #    new_pathfilename = PathFilename(base_path=base_path, position=0, previous_position=None)
    #    new_pathfilename.filename = Filename.construct(session=session, filename=filename)
    #    self.pathfilenames.append(pathfilename)
    #    session.add(self)
    #    session.flush(objects=[self])
