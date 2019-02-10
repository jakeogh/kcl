#!/usr/bin/env python3

import struct
import socket


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def validate_ipv4(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error as e:
#       raise e
        return False


def normalize_ipv4(addr):
    if validate_ipv4(addr):
        return int2ip(ip2int(addr))

#if __name__ == '__main__':
#    import sys
#    normalized_ipv4 = normalize_ipv4(sys.argv[1])
#    if normalized_ipv4:
#        print(normalized_ipv4)
#        quit(0)
#    quit(1)

