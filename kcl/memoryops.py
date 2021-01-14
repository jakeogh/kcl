#!/usr/bin/env python3

import os

from icecream import ic

from kcl.commandops import run_command


def pmap():
    command = ['pmap', str(os.getpid())]
    result = run_command(command).decode('utf8')
    result = result.split('\n')
    result = result[-1]
    result = result.split(' ')
    result = result[-1]
    return result
