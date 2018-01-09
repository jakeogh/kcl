#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
'''
Filename class
'''

from sqlalchemy import Column
from sqlalchemy import CheckConstraint
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.hybrid import hybrid_property
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.sqlalchemy.BaseMixin import BASE

from sqlalchemy.ext.hybrid import Comparator


#class CaseInsensitiveComparator(Comparator):
#    def __eq__(self, other):
#        return func.lower(self.__clause_element__()) == func.lower(other)


# https://www.postgresql.org/docs/current/static/datatype-binary.html
# https://www.postgresql.org/docs/current/static/functions-binarystring.html
# https://stackoverflow.com/questions/6637843/query-bytea-field-in-postgres-via-command-line
# https://dba.stackexchange.com/questions/130812/query-bytea-column-using-prefix
# https://www.postgresql.org/message-id/1657180000.1070472048%40gnarzelwicht.delirium-arts.de
# https://anonscm.debian.org/cgit/collab-maint/musl.git/tree/src/ctype/tolower.c
# https://docs.python.org/3.6/library/os.html#file-names-command-line-arguments-and-environment-variables

class Filename(BASE):
    '''
    UNIX filenames can be anything but NULL and / therefore a binary type is required.
    max file name length is 255 on all UNIX-like filesystems
    this does not store the path to the filename, so / is not allowed

    Most filesystems do not _have_ a byte encoding, all bytes but NULL are valid in a path.
    The user enviroment might interperit the names with a encoding like UTF8, but this has
    no effect on what bytes are possible to store in filenames.

    '''
    id = Column(Integer, primary_key=True)

    filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0" #todo test
    filename = Column(BYTEA(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)

    @classmethod
    def construct(cls, *, session, filename):
        if isinstance(filename, str):
            filename = bytes(filename, encoding='UTF8')  # handle command line input
        result = get_one_or_create(session, Filename, filename=filename)
        return result

    # because I cant figure out how to get the orm to emit:
    # bytes(session.execute("SELECT filename FROM filename WHERE encode(filename, 'escape') ILIKE encode('%JaguarAJ-V8EnginE%'::bytea, 'escape')").scalar())
    # https://docs.python.org/3/library/stdtypes.html#bytes.lower
    # https://github.com/python/cpython/blob/43ba8861e0ad044efafa46a7cc04e12ac5df640e/Objects/bytes_methods.c#L248
    # https://github.com/python/cpython/blob/6f0eb93183519024cb360162bdd81b9faec97ba6/Include/pyctype.h#L29
    # https://github.com/python/cpython/blob/6f0eb93183519024cb360162bdd81b9faec97ba6/Python/pyctype.c#L145
    # lower() on a bytes object maps 0x41-0x5a to 0x61-0x7a
    @hybrid_property
    def filename_lower(self):
        #return bytes(self.filename).lower() #nope, sqlalchemy cant translate because LOWER() is not defined for bytea
        latin1_str = str(bytes(self.filename), encoding='Latin1').lower()
        print("latin1_str:", latin1_str)
        return latin1_str

#    @filename_lower.comparator
#    def word_insensitive(cls):
#        return CaseInsensitiveComparator(cls.filename)


    def __repr__(self):
        return "<Filename(id=%s filename=%s)>" % (str(self.id), str(self.filename))

    def __bytes__(self):
        return self.filename

