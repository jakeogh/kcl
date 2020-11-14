#!/usr/bin/env python3

import time
#import errno as error_number
from icecream import ic


def retry_on_exception(*,
                       function,
                       exceptions,
                       errno,
                       kwargs={},
                       delay=1,
                       verbose=False,
                       delay_multiplier=0.5,):

    if not isinstance(exceptions, tuple):
        raise ValueError('exceptions must be a tuple, not:', type(exceptions))
    while True:
        try:
            return function(**kwargs)
            break
        except exceptions as e:
            #if verbose:
            ic(e, e.errno)
            if not e.errno == errno:
                raise e
            ic(function)
            ic(e)
            ic(exceptions)
            #print(e, file=sys.stderr)
            delay = delay + (delay * delay_multiplier)
            ic(delay)
            time.sleep(delay)

