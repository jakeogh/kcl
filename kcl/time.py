#!/usr/bin/env python3

import time

def timestamp():
    timestamp = str("%.22f" % time.time())
    return timestamp

if __name__ == '__main__':
    timestamp = timestamp()
    print(timestamp)
