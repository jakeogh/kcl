#!/usr/bin/env python

#from IPython import embed; embed()
import ipdb


def embed_ipython():
    ipdb.set_trace()


def pause(message, ipython=False):
    assert isinstance(message, str)
    if ipython:
        message += " (type 'ipython' to enter shell): "
    response = input(message)
    if response == "ipython":
        embed_ipython()
        pause("press enter to continue execution")

