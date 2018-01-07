#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License

from sqlalchemy.orm.exc import NoResultFound
from .Filename import Filename
from .PathFilename import PathFilename
from kcl.printops import ceprint

def find_path(session, path):
    ceprint("path:", path)
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

    try:
        for index, filename in enumerate(path_split):
            ceprint(index, filename)
            filename = session.query(Filename).filter_by(filename=filename).one()
            ceprint("filename:", filename)
            pathfilename_list = session.query(PathFilename).filter_by(filename=filename, position=index).all()
            ceprint("pathfilename_list:")
            for pf in pathfilename_list:
                ceprint(pf)
            ceprint("pathfilename_list:", pathfilename_list)
            if pathfilename_list:
                pathfilename_list_path_set = set([pathfilename.filename for pathfilename in pathfilename_list])
                ceprint("pathfilename_list_path_set:", pathfilename_list_path_set)
                if not possible_path_set:
                    possible_path_set = pathfilename_list_path_set
                    ceprint("*possible_path_set:", possible_path_set)
                else:
                    possible_path_set = possible_path_set & pathfilename_list_path_set
                    ceprint("possible_path_set:", possible_path_set)
                for pathfilename in pathfilename_list:
                    if index == 0:  # only add paths that start with the correct filename
                        possible_path_set.add(pathfilename.path)
                    else:
                        if pathfilename.path not in possible_path_set:
                            return False
                if not possible_path_set:
                    return False
                if len(possible_path_set) == 1:
                    last_path = list(possible_path_set)[0]
                    last_path_text = str(last_path)
                    if last_path_text == path:
                        return last_path
                    return False
    except NoResultFound:  # any failed query
        ceprint("NoResultFound returning False")
        return False
