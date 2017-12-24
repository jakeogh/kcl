#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from sqlalchemy import Table
from sqlalchemy import Column           #                                                                                                                               http://docs.sqlalchemy.org/en/rel_0_9/core/metadata.html#sqlalchemy.schema.Column
from sqlalchemy import ForeignKey       #                                                                                                                               http://docs.sqlalchemy.org/en/rel_0_9/core/metadata.html#sqlalchemy.schema.Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint  #                                                                                                                               http://docs.sqlalchemy.org/en/rel_0_9/core/constraints.html#check-constraint

from sqlalchemy import Integer          # int4 integer    4 bytes -2147483648 to +2147483647 1,400,384,814(typical timestamp)                                           http://docs.sqlalchemy.org/en/rel_0_9/core/type_basics.html#sqlalchemy.types.uInteger
from sqlalchemy import BigInteger       # int8 bigint     8 bytes -9223372036854775808 to +9223372036854775807                                                          http://www.postgresql.org/docs/9.4/static/datatype-numeric.html
from sqlalchemy import String           #The base for all string and character types. In SQL, corresponds to VARCHAR. Can also take py unicode is db bind set           http://docs.sqlalchemy.org/en/rel_0_9/core/type_basics.html#sqlalchemy.types.String
from sqlalchemy import UnicodeText      #An unbounded-length Unicode string type.
from sqlalchemy import Unicode          #The Unicode type is a String subclass that assumes input and output as Python unicode data                                     http://docs.sqlalchemy.org/en/rel_0_9/core/type_basics.html#sqlalchemy.types.Unicode
                                        #in pgsql this is VARCHAR: http://www.postgresql.org/docs/9.2/static/datatype-character.html
from sqlalchemy import Numeric          #A type for fixed precision numbers, such as NUMERIC or DECIMAL.                                                                http://docs.sqlalchemy.org/en/rel_0_9/core/type_basics.html#sqlalchemy.types.Numeric
from sqlalchemy import Enum             #Generic Enum Type. By default, uses the backend’s native ENUM type if available, else uses VARCHAR + a CHECK constraint.       http://docs.sqlalchemy.org/en/rel_0_9/core/type_basics.html#sqlalchemy.types.Enum
#from sqlalchemy import LargeBinary      #A type for large binary byte data. PG: bytea (i think)                                                                         http://www.postgresql.org/docs/9.4/static/datatype-binary.html
#from sqlalchemy.types import BINARY     #SQL BINARY type                                                                                                                http://docs.sqlalchemy.org/en/rel_1_0/core/type_basics.html#sqlalchemy.types.BINARY
#from sqlalchemy.types import CHAR       #fixed length string (unicode?)                                                                                                 http://www.postgresql.org/docs/9.4/static/datatype-character.html
#from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Sequence
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.model.Filename import Filename
from kcl.sqlalchemy.model.Path import Path
from kcl.sqlalchemy.model.BytesHash import BytesHash
from kcl.sqlalchemy.model.Timestamp import Timestamp
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.printops import eprint
from kcl.fileops import is_regular_file
from kcl.hashops import generate_hash
from sqlalchemy.orm.exc import NoResultFound

class FileRecord(BASE):
    '''
    Combination of:
        Filename
        Path
        metadata
    '''

    id = Column(Integer, Sequence('id_seq', start=0, minvalue=0), autoincrement=True, primary_key=True, index=True)

    path_id = Column(Integer, ForeignKey('path.id'), unique=False, nullable=False, index=True)
    path = relationship('Path', backref='files')

    symlink_target_path_id = Column(Integer, ForeignKey('path.id'), unique=False, nullable=True, index=True)
    symlink_target_path = relationship('Path', foreign_keys=[symlink_target_path_id], backref='targets')

    #EmployeeID = Column(Integer, ForeignKey('Employee.EmployeeId'), primary_key=True)
    #employee = relationship('Employee', foreign_keys=[EmployeeID], backref='Employee')

    #OldemployeeID = Column(Integer, ForeignKey('Employee.EmployeeId'))
    #old_employee = relationship("Employee", foreign_keys=[OldemployeeID], backref='Employee')



    filename_id = Column(Integer, ForeignKey('filename.id'), unique=False, nullable=False, index=True)
    filename = relationship('Filename', backref='files')

    byteshash_id = Column(Integer, ForeignKey('byteshash.id'), unique=False, nullable=False, index=True)
    byteshash = relationship('BytesHash', backref='files')

    timestamp_id = Column(Integer, ForeignKey('timestamp.id'), unique=True, nullable=False, index=True)
    timestamp = relationship('Timestamp', backref='file')

    #stat_st_modes = ('S_ISDIR',
    #                 'S_ISCHR',
    #                 'S_ISBLK',
    #                 'S_ISREG',
    #                 'S_ISFIFO',
    #                 'S_ISLNK',
    #                 'S_ISSOCK',
    #                 'S_ISDOOR',
    #                 'S_ISPORT',
    #                 'S_ISWHT')
    #stat_st_mode = Column(Enum(*stat_st_modes, name='stat_st_modes_enum'), unique=False, nullable=False, index=True)

    stat_st_mode  = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_inode = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_dev   = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_nlink = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_uid   = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_gid   = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_size  = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_atime = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_mtime = Column(Integer,    unique=False, nullable=False, index=True)
    stat_st_ctime = Column(Integer,    unique=False, nullable=False, index=True)

    @classmethod
    def construct(cls, session, inpath, debug=False):
        assert isinstance(inpath, bytes)
        inpath = os.path.abspath(inpath) #click.Path does all this
        path, filename = os.path.split(inpath)
        stat = os.stat(inpath)
        if is_regular_file(inpath): #this stuff should be in BytesHash.construct
            if stat.st_size > 0:
                if stat.st_size >= 1024*1024*1024: #1GB
                    print("hashing file >1GB:", path, str(stat.st_size/1024.0/1024.0/1024.0)+'GB')
                    if stat.st_size >= 1024*1024*1024*1024: #1TB
                        print("skipping file >=1TB:", path)
                        #skipped_file_list.append(path)
                    else:
                        data_hash = generate_hash(path)
                else: #not a big file
                    data_hash = generate_hash(path)


        path      = Path.construct(session, path=path)
        filename  = Filename.construct(session, filename=filename)
        # hash the file _every time_
        byteshash  = BytesHash.construct(session, bytes_like_object=inpath)
        timestamp = Timestamp.construct(session)
        result = get_one_or_create(session, FileRecord, path=path,
                                                        filename=filename,
                                                        byteshash=byteshash,
                                                        timestamp=timestamp,
                                                        stat_st_mode=stat.st_mode,
                                                        stat_st_inode=stat.st_ino,
                                                        stat_st_dev=stat.st_dev,
                                                        stat_st_nlink=stat.st_nlink,
                                                        stat_st_uid=stat.st_uid,
                                                        stat_st_gid=stat.st_gid,
                                                        stat_st_size=stat.st_size,
                                                        stat_st_atime=stat.st_atime,
                                                        stat_st_mtime=stat.st_mtime,
                                                        stat_st_ctime=stat.st_ctime)

        return result

    def __bytes__(self):
        return b'/'.join([bytes(self.path), bytes(self.filename)])

    #@hybrid_property
    #def tags(self):
    #    tags = []
    #    for bookmark in self.bookmarks:
    #        for tag in bookmark.tags:
    #            tags.append(tag)
    #    return set(tags)

    #@hybrid_property
    #def plugin_outputs(self):
    #    plugin_outputs = []
    #    for bookmark in self.bookmarks:
    #        for plugin_output in bookmark.plugin_outputs:
    #            plugin_outputs.append(plugin_output)
    #    return set(plugin_outputs)

    #@hybrid_property
    #def datas(self):
    #    datas = []
    #    for plugin_output in self.plugin_outputs:
    #        datas.append(plugin_output.data)
    #    return set(datas)

    #@hybrid_property
    #def data_hashes(self):
    #    hashes = []
    #    for data in self.datas:
    #        hashes.append(data.hash)
    #    return set(hashes)

    #@hybrid_property
    #def hash(self):
    #    return self.iri.hash
