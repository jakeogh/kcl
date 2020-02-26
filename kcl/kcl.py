#!/usr/bin/env python3

import builtins
from .Config import CONFIG
builtins.config = CONFIG

from kcl.sqlalchemy.clickapp.clickapp import clickapp as kcl
kcl.help = CONFIG.appname + " interface"
CONFIG.appobject = kcl

from kcl.sqlalchemy.clickapp.default import *

from .cli._htmlops._htmlops import _htmlops
from .cli._redisops._redisops import _redisops
from .cli._dirops._dirops import _dirops

kcl.add_command(_htmlops, name='htmlops')
kcl.add_command(_redisops, name='redisops')
kcl.add_command(_dirops, name='dirops')
