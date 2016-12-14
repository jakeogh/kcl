#!/usr/bin/env python3

import logging
import os
import sys
import time
import inspect

class logmaker():
    def __init__(self, output_format, name, level):
        self.logger = logging.getLogger(name)
        self.logger_ch = logging.StreamHandler()
        self.formatter = logging.Formatter(output_format)
        self.logger_ch.setFormatter(self.formatter)
        self.logger.addHandler(self.logger_ch)
        self.logger.setLevel(level)

LOG = {
    'CRITICAL': logging.CRITICAL, # 50
    'ERROR':    logging.ERROR,    # 40
    'WARNING':  logging.WARNING,  # 30  # python default level
    'INFO':     logging.INFO,     # 20
    'DEBUG':    logging.DEBUG     # 10
    }

FORMAT = "%(levelname)-5s %(lineno)4s %(filename)-18s:%(funcName)-13s : %(message)s"
QUIET_FORMAT = "%(message)s"
logger_quiet = logmaker(output_format=QUIET_FORMAT, name="logging_quiet",
    level=LOG['INFO'])


def eprint(*args, level, **kwargs):
    if level == LOG['INFO']:
        logger_quiet.logger.info(*args, **kwargs)
    elif level >= LOG['WARNING']:
        logger_quiet.logger.warning(*args, **kwargs)

def set_verbose(ctx, param, verbose=False):
    if verbose:
        logger_quiet.logger.setLevel(LOG['DEBUG'])
    else:
        logger_quiet.logger.setLevel(LOG['INFO'] + 1)


def cprint(*args, **kwargs):
    caller = sys._getframe(1).f_code.co_name
    frm = inspect.stack()[1]
    mod = str(inspect.getmodule(frm[0]))
    source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    #print("source_file:", source_file)
    print(str("%.5f" % time.time()), os.getpid(), source_file, '{0: <29}'.format(caller+'()'), *args, file=sys.stderr, **kwargs)



