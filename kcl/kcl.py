#!/usr/bin/env python3

import builtins
from kcl.model.Config import CONFIG
builtins.config = CONFIG


from kcl.sqlalchemy.clickapp.ClickApp import clickapp
from kcl.sqlalchemy.ipython import ipython
#from kcl.sqlalchemy.visualization.sa_display import sa_display

clickapp.help = CONFIG.appname + " interface"
clickapp.add_command(ipython)
#clickapp.add_command(sa_display)

