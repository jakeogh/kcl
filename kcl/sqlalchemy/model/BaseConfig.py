#!/usr/bin/env python3

import os
import time
import attr

@attr.s
class BaseConfig():
    '''Simple configuration class.'''
    def __init__(self):
        self.db_uri = 'postgresql://postgres@localhost/'
        self.dbpath_postgres = self.db_uri + 'postgres'
        self.dbname_timestamp = 'test_' + str(time.time()).replace('.', '_')
        self.database_timestamp = self.db_uri + self.dbname_timestamp
        self.database_echo = False
    def database_real(self, dbname):
        self.database_real = self.db_uri + dbname
        return self.database_real

BASECONFIG = BaseConfig()
