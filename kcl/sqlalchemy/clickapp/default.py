#!/usr/bin/env python3

import builtins
CONFIG = builtins.config

from kcl.sqlalchemy.clickapp.ipython import ipython
CONFIG.appobject.add_command(ipython)

from kcl.sqlalchemy.clickapp.print_database import print_database
CONFIG.appobject.add_command(print_database)

from kcl.sqlalchemy.clickapp.show_config import show_config
CONFIG.appobject.add_command(show_config)

from kcl.sqlalchemy.clickapp.test import test
CONFIG.appobject.add_command(test)