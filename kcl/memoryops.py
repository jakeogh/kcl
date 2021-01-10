#!/usr/bin/env python3

import os

from icecream import ic

from .commandops import execute_command


def pmap():
    command = ['pmap', os.getpid()]
    result = execute_command(command)
    return result
