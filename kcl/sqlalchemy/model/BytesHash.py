#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
from sqlalchemy import Column
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.schema import Sequence
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.get_one_or_create import get_one_or_create
from kcl.hashops import bytes_dict_file
from kcl.hashops import bytes_dict_bytes


class BytesHash(BASE):
    __table_args__ = (UniqueConstraint('md5', 'ripemd160', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'whirlpool'),)
    id = Column(BigInteger, Sequence('id_seq', start=0, minvalue=0), autoincrement=True, primary_key=True, index=True)

    # MD5 is heka-broken
    md5       = Column(BYTEA(16), CheckConstraint('octet_length(md5)       = 16'), unique=False, nullable=True, index=True)
    ripemd160 = Column(BYTEA(20), CheckConstraint('octet_length(ripemd160) = 20'), unique=True, nullable=True, index=True)
    # SHA1 is broken
    # SHA1 is heka-broken https://security.googleblog.com/2017/02/announcing-first-sha1-collision.html
    sha1      = Column(BYTEA(20), CheckConstraint('octet_length(sha1)      = 20'), unique=False, nullable=False, index=True)
    sha224    = Column(BYTEA(28), CheckConstraint('octet_length(sha224)    = 28'), unique=True, nullable=True, index=True)
    sha256    = Column(BYTEA(32), CheckConstraint('octet_length(sha256)    = 32'), unique=True, nullable=True, index=True)
    sha384    = Column(BYTEA(48), CheckConstraint('octet_length(sha384)    = 48'), unique=True, nullable=True, index=True)
    sha512    = Column(BYTEA(64), CheckConstraint('octet_length(sha512)    = 64'), unique=True, nullable=True, index=True)
    whirlpool = Column(BYTEA(64), CheckConstraint('octet_length(whirlpool) = 64'), unique=True, nullable=False, index=True)
    # gotta move to 3.6 to use blake2
    # https://docs.python.org/3.6/library/hashlib.html
    #blake2    = Column(BYTEA(64), CheckConstraint('octet_length(blake2)    = 64'), unique=True, nullable=True, index=True)

    @classmethod
    def construct(cls, session, bytes_like_object):
        if isinstance(bytes_like_object, bytes):
            bytes_dict = bytes_dict_bytes(bytes_like_object)
        else:
            bytes_dict = bytes_dict_file(bytes_like_object)
        import IPython; IPython.embed()
        byteshash = get_one_or_create(session, Hash, **bytes_dict)
        return byteshash

    def __repr__(self):
        return str(binascii.hexlify(self.whirlpool))
