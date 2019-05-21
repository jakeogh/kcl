#!/usr/bin/env python3

import builtins
CONFIG = builtins.config

from kcl.printops import eprint
from kcl.printops import ceprint


from kcl.sqlalchemy.clickapp.cli.debug.debug import debug
CONFIG.appobject.add_command(debug)

#from kcl.sqlalchemy.clickapp.cli._mcreate._mcreate import _mcreate
#CONFIG.appobject.add_command(_mcreate)

from kcl.sqlalchemy.clickapp.test import test
CONFIG.appobject.add_command(test)
ceprint("here")
