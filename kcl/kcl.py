#!/usr/bin/env python3

from kcl.sqlalchemy.clickapp.ClickApp import ClickApp
from kcl.model.Config import CONFIG

CA = ClickApp(config=CONFIG)
clickapp = CA.clickapp

