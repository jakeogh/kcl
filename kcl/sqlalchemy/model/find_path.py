#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

from sqlalchemy.orm.exc import NoResultFound
from .Filename import Filename
from .PathFilename import PathFilename
from kcl.printops import ceprint
from kcl.printops import eprint

def find_path(session, path):
    #ceprint("path:", path)
    '''
    iterates over the pathfilenames table to check for a existing path
    returns the path if found, else returns False
    it's reasonable to return the path if it's found beacuse unlike an alias, a path cant point to
    the wrong thing. returning a "duplicate" alias only makes sense if it's pointing to the same path.
    '''
    possible_path_set = set([])
    assert isinstance(path, bytes)
    path_split = path.split(b'/')
    assert path_split
    #ceprint("path_split:", path_split)

    if path_split[-1] == b'':
        eprint("special case for /")
    if path.startswith(b'/'):
        absolute = True
    else:
        absolute = False

    try:
        for index, filename in enumerate(path_split):
            #ceprint(index, filename)
            if absolute and index == 0:
                continue  # skip matching every single absolute pathfilename
            filename = session.query(Filename).filter_by(filename=filename).one()
            #ceprint("filename:", filename)

            pathfilenames_with_filename_in_correct_position = \
                session.query(PathFilename).filter_by(filename=filename, position=index).all()
            #ceprint("pathfilenames_with_filename_in_correct_position:")
            for pf in pathfilenames_with_filename_in_correct_position: print('\t', pf)

            paths_that_match_filename = \
                set([pathfilename.path for pathfilename in pathfilenames_with_filename_in_correct_position])
            if paths_that_match_filename:
                #ceprint("paths_that_match_filename:")
                for pf in paths_that_match_filename: #ceprint('\t', pf)

            if len(possible_path_set) == 0:
                possible_path_set = paths_that_match_filename
            else:
                possible_path_set = possible_path_set & paths_that_match_filename  # intersection

            for pathfilename in pathfilenames_with_filename_in_correct_position:
                if pathfilename.path not in possible_path_set:
                    #ceprint("pathfilename.path", pathfilename.path, "not in possible_path_set, returning False")
                    return False

            if not possible_path_set:
                #ceprint("empty possible_path_set, returning False")
                return False

            if len(possible_path_set) == 1:
                only_path = list(possible_path_set)[0]
                #ceprint("only_path:", only_path, "path:", path)
                if only_path.path == path:
                    #ceprint("returning only_path:", only_path)
                    return only_path
                #ceprint("returning False")
                return False

        # ran out of path elements to loop through
        # if there are any paths left in possible_path_set, then it _must_ contain the match
        for possible_path in possible_path_set:
            if possible_path.path == path:
                return possible_path

        if possible_path_set:
            assert False  # shouldnt happen

    except NoResultFound:  # any failed query
        #ceprint("NoResultFound returning False")
        return False
