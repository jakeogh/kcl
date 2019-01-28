#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
'''
    Config class
'''
from kcl.sqlalchemy.model.BaseConfig import BaseConfig

import attr

@attr.s(auto_attribs=True)
class Config(BaseConfig):
    appname: str = "kcl"
    def __attrs_post_init__(self):
        BaseConfig.__init__(self)

CONFIG = Config()
