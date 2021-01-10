#!/usr/bin/env python3

import os

from icecream import ic

from kcl.commandops import run_command


def pmap():
    command = ['pmap', os.getpid()]
    result = run_command(command)
    return result
