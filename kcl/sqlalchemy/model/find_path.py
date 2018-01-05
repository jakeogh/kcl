#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

from sqlalchemy.orm.exc import NoResultFound
from .Filename import Filename
from .PathFilename import PathFilename

def find_path(session, path):
    '''
    iterates over the pathfilenames table to check for a existing path
    returns the path if found, else returns False
    it's reasonable to return the path if it's found beacuse unlike an alias, a path cant point to
    the wrong thing. returning a "duplicate" alias only makes sense if it's pointing to the same path.
    '''
    corrected_path = path
    possible_path_set = set([])
    assert isinstance(path, bytes)

    corrected_path = path
    corrected_path_split = corrected_path.split(b'/')

    try:
        for index, filename in enumerate(corrected_path_split):
            current_filename = session.query(Filename).filter_by(filename=filename).one()
            current_pathfilename_list = session.query(PathFilename).filter_by(filename=current_filename, position=index).all()
            if current_pathfilename_list:
                current_pathfilename_list_path_set = set([pathfilename.path for pathfilename in current_pathfilename_list])
                if not possible_path_set:
                    possible_path_set = current_pathfilename_list_path_set
                else:
                    possible_path_set = possible_path_set & current_pathfilename_list_path_set
                for pathfilename in current_pathfilename_list:
                    if index == 0: # only add paths that start with the correct filename
                        possible_path_set.add(pathfilename.path)
                    else:
                        if pathfilename.path not in possible_path_set:
                            return False
                if not possible_path_set:
                    return False
                if len(possible_path_set) == 1:
                    last_path = list(possible_path_set)[0]
                    last_path_text = str(last_path)
                    if last_path_text == corrected_path:
                        return last_path
                    return False
    except NoResultFound: # any failed query
        #print("NoResultFound returning False")
        return False
