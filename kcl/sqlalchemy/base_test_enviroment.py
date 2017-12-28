#!/usr/bin/env python3

import pprint
pp = pprint.PrettyPrinter(indent=4)
from kcl.sqlalchemy.delete_database import delete_database
from kcl.sqlalchemy.check_db_result import check_db_result
from kcl.sqlalchemy.BaseMixin import BASE
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.printops import eprint

import logging
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
