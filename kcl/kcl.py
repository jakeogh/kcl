#!/usr/bin/env python3

from kcl.sqlalchemy.clickapp.ClickApp import ClickApp
from kcl.model.Config import CONFIG
from kcl.sqlalchemy.ipython import ipython

CA = ClickApp(config=CONFIG)
clickapp = CA.clickapp
clickapp.help = CONFIG.appname + " interface"

clickapp.add_command(ipython)
