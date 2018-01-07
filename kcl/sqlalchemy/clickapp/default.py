#!/usr/bin/env python3

import builtins
CONFIG = builtins.config

from kcl.printops import eprint

from kcl.sqlalchemy.clickapp.cli.debug.debug import debug
CONFIG.appobject.add_command(debug)

#from kcl.sqlalchemy.clickapp.cli.database.database import database
#CONFIG.appobject.add_command(database)

#from kcl.sqlalchemy.clickapp.show_config import show_config
#CONFIG.appobject.add_command(show_config)

from kcl.sqlalchemy.clickapp.test import test
CONFIG.appobject.add_command(test)
