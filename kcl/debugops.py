#!/usr/bin/env python3

#from IPython import embed; embed()


def embed_ipdb():
    import ipdb
    ipdb.set_trace()


def pause(message='', ipython=False):
    assert isinstance(message, str)
    if ipython:
        message += " (type 'ipython' to enter shell or 'ipdb' to enter debugger): "
    response = input(message)
    if response == "ipdb":
        embed_ipdb()
        pause("press enter to continue execution")
    elif response == "ipython":
        from IPython import embed; embed()
        pause("press enter to continue execution")
