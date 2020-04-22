#!/usr/bin/env python3

import os

def set_process_lowest_priority():
    os.setpriority(os.PRIO_PROCESS, 0, 19)
