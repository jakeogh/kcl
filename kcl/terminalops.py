#!/usr/bin/env python3

import shutil

def get_terminal_width(default=80):
    width, height = shutil.get_terminal_size((default, 20))
    return width

