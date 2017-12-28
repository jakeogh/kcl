#!/usr/bin/env python3

#from kcl.sqlalchemy.clickapp.clickapp import clickapp
from kcl.sqlalchemy.clickapp.ClickApp import ClickApp
#from kcl.sqlalchemy.model.BaseConfig import BASECONFIG as CONFIG
from kcl.model.Config import CONFIG

CA = ClickApp(config=CONFIG)
clickapp = CA.clickapp
