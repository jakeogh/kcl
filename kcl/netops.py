#!/usr/bin/env python3

import requests
from kcl.assertops import verify
from kcl.printops import eprint


def download_file(url, destination_dir, force=False, proxy=None):
    eprint("downloading:", url)
    local_filename = destination_dir + '/' + url.split('/')[-1]
    #if force:
    #    os.unlink(local_filename)
    proxy_dict = {}
    if proxy:
        verify(proxy.startswith('http'))
        verify(len(proxy.split(":")) == 3)
        proxy_dict["http"] = proxy
        proxy_dict["https"] = proxy

    r = requests.get(url, stream=True, proxies=proxy_dict)
    try:
        with open(local_filename, 'bx') as fh:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    fh.write(chunk)
    except FileExistsError:
        eprint("skipping download, file exists:", local_filename)
    r.close()
    return local_filename

