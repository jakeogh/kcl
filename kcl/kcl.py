#!/usr/bin/env python3

import builtins
from kcl.Config import CONFIG
builtins.config = CONFIG

from kcl.sqlalchemy.clickapp.clickapp import clickapp as kcl
kcl.help = CONFIG.appname + " interface"
CONFIG.appobject = kcl

from kcl.sqlalchemy.clickapp.default import *

from .cli._htmlops._htmlops import _htmlops

kcl.add_command(_htmlops, name='htmlops')

#from kcl.sqlalchemy.visualization.sa_display import sa_display
#kcl.add_command(sa_display)

