#!/usr/bin/env python3

#from kcl.sqlalchemy.clickapp.clickapp import clickapp
from kcl.sqlalchemy.clickapp.ClickApp import ClickApp
from kcl.sqlalchemy.model.BaseConfig import BASECONFIG as CONFIG

CA = ClickApp(config=config)
clickapp = CA.clickapp
