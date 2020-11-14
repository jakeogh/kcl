#!/usr/bin/env python3

import time
from icecream import ic


def retry_on_exception(*, function, exceptions, kwargs={}, delay=1, delay_multiplier=0.5):
    if not isinstance(exceptions, tuple):
        raise ValueError('exceptions must be a tuple, not:', type(exceptions))
    while True:
        try:
            return function(**kwargs)
            break
        except exceptions as e:
            ic(e)
            ic(exceptions)
            #print(e, file=sys.stderr)
            delay = delay + (delay * delay_multiplier)
            ic(delay)
            time.sleep(delay)

