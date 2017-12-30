#!/usr/bin/env python3

import builtins
from kcl.model.Config import CONFIG
builtins.config = CONFIG

from kcl.sqlalchemy.clickapp.clickapp import clickapp as kcl
from kcl.sqlalchemy.ipython import ipython
#from kcl.sqlalchemy.visualization.sa_display import sa_display

kcl.help = CONFIG.appname + " interface"
kcl.add_command(ipython)
#clickapp.add_command(sa_display)

