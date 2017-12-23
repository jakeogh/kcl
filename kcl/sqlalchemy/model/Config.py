#!/usr/bin/env python3
import os
import time

class Config():
    '''Simple configuration class.'''
    def __init__(self):
        self.db_uri = 'postgresql://postgres@localhost/'
        self.dbpath_postgres = self.db_uri + 'postgres'
        self.dbname_timestamp = 'test_' + str(time.time()).replace('.', '_')
        self.database_timestamp = self.db_uri + self.dbname_timestamp

CONFIG = Config()
