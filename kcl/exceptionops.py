#!/usr/bin/env python3

import sys
import time


def retry_on_exception(*, function, exception, kwargs={}, delay=1, delay_multiplier=0.5):
    while True:
        try:
            return exec(function(**kwargs))  # I need to return what function returned, not None that exec returns
            break
        except exception as e:
            print(e, file=sys.stderr)
            delay = delay + (delay * delay_multiplier)
            time.sleep(delay)

