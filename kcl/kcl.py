#!/usr/bin/env python3

import builtins
from kcl.sqlalchemy.clickapp.ClickApp import clickapp
from kcl.model.Config import CONFIG
builtins.config = CONFIG
from kcl.sqlalchemy.ipython import ipython

#CA = ClickApp(config=CONFIG)
#clickapp = CA.clickapp
clickapp.help = CONFIG.appname + " interface"

clickapp.add_command(ipython)
