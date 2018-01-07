#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.model.Filename import Filename
from kcl.sqlalchemy.model.Path import Path
from kcl.sqlalchemy.model.BytesHash import BytesHash
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.printops import eprint
from kcl.fileops import is_regular_file
from kcl.symlinkops import is_symlink
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func

class FileRecord(BASE):
    '''
    Combination of:
        Filename
        Path
        metadata
    '''
    id = Column(Integer, Sequence('id_seq', start=0, minvalue=0), autoincrement=True, primary_key=True, index=True)

    path_id = Column(Integer, ForeignKey('path.id'), unique=False, nullable=False, index=True)
    path = relationship('Path', foreign_keys=[path_id], backref='filerecords')

    symlink_target_path_id = Column(Integer, ForeignKey('path.id'), unique=False, nullable=True, index=True)
    symlink_target_path = relationship('Path', foreign_keys=[symlink_target_path_id], backref='targets')

    filename_id = Column(Integer, ForeignKey('filename.id'), unique=False, nullable=False, index=True)
    filename = relationship('Filename', backref='filerecords')

    byteshash_id = Column(Integer, ForeignKey('byteshash.id'), unique=False, nullable=True, index=True)
    byteshash = relationship('BytesHash', backref='filerecords')

    timestamp = Column(DateTime(timezone=True), unique=False, nullable=False, index=True, server_default=func.now())

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

    stat_st_mode = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_inode = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_dev = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_nlink = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_uid = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_gid = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_size = Column(BigInteger, unique=False, nullable=False, index=True)
    stat_st_atime = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_mtime = Column(Integer, unique=False, nullable=False, index=True)
    stat_st_ctime = Column(Integer, unique=False, nullable=False, index=True)

    @classmethod
    def construct(cls, session, path):
        #eprint("path:", path)
        if not isinstance(path, bytes):
            path = bytes(path, encoding='UTF8') # allow command line args
        abspath = os.path.abspath(path)
        assert abspath.startswith(b'/')
        path, filename = os.path.split(abspath)
        stat = os.stat(abspath, follow_symlinks=False)

        path = Path.construct(session=session, path=path)
        filename = Filename.construct(session=session, filename=filename)

        if is_regular_file(abspath): #this stuff should be in BytesHash.construct
            if stat.st_size == 0:
                byteshash = None
            else:
                if stat.st_size >= 1024*1024*1024: #1GB
                    print("hashing file >1GB:", path, str(stat.st_size/1024.0/1024.0/1024.0)+'GB')
                    if stat.st_size >= 1024*1024*1024*1024: #1TB
                        print("skipping file >=1TB:", path)
                        #skipped_file_list.append(path)
                    else:
                        byteshash = BytesHash.construct(session, bytes_like_object=abspath)
                else: #not a big file
                    byteshash = BytesHash.construct(session, bytes_like_object=abspath)
        else:
            byteshash = None

        if is_symlink(abspath):
            symlink_target = os.readlink(abspath)
            symlink_target_path = Path.construct(session=session, path=symlink_target)
        else:
            symlink_target_path = None

        #import IPython; IPython.embed()
        # pointless to use get_one_or_create due to using a timestamp
        result = get_one_or_create(session, FileRecord, path=path,
                                   filename=filename,
                                   symlink_target_path=symlink_target_path,
                                   byteshash=byteshash,
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
        #import IPython; IPython.embed()
        outfile = b'/'.join([bytes(self.path), bytes(self.filename)])
        if self.symlink_target_path:
            outfile = b' -> '.join([outfile, bytes(self.symlink_target_path)])
        return outfile

    def __repr__(self):
        return "<FileRecord(id=%s path=%s filename=%s byteshash=%s)>" % (str(self.id), str(self.path), str(self.filename), str(self.byteshash))

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
