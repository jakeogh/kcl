#!/usr/bin/env python3

import builtins
from kcl.Config import CONFIG
builtins.config = CONFIG

from kcl.sqlalchemy.clickapp.clickapp import clickapp as kcl
kcl.help = CONFIG.appname + " interface"
CONFIG.appobject = kcl

from kcl.sqlalchemy.clickapp.default import *

from .cli._htmlops._htmlops import _htmlops
from .cli._redisops._redisops import _redisops

kcl.add_command(_htmlops, name='htmlops')
kcl.add_command(_redisops, name='redisops')
