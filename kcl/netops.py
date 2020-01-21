#!/usr/bin/env python3

import requests
from icecream import ic
#from kcl.assertops import verify
from kcl.printops import eprint
from kcl.fileops import read_file_bytes


def construct_proxy_dict():
    proxy_config = read_file_bytes('/etc/portage/proxy.conf').decode('utf8').split('\n')
    ic(proxy_config)
    proxy_dict = {}
    for line in proxy_config:
        ic(line)
        scheme = line.split('=')[0].split('_')[0]
        line = line.split('=')[-1]
        line = line.strip('"')
        #scheme = line.split('://')[0]
        ic(scheme)
        proxy_dict[scheme] = line
        #proxy = line.split('://')[-1].split('"')[0]
    return proxy_dict


def download_file(url, destination_dir=None, force=False, proxy_dict=None):
    eprint("downloading:", url)
    if destination_dir:
        local_filename = destination_dir + '/' + url.split('/')[-1]
    else:
        local_filename = None

    #if force:
    #    os.unlink(local_filename)

    #proxy_dict = {}
    #if proxy:
    #    verify(not proxy.startswith('http'))
    #    verify(len(proxy.split(":")) == 2)
    #    proxy_dict["http"] = proxy
    #    proxy_dict["https"] = proxy

    ic(proxy_dict)
    r = requests.get(url, stream=True, proxies=proxy_dict)
    if local_filename:
        try:
            with open(local_filename, 'bx') as fh:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        fh.write(chunk)
        except FileExistsError:
            eprint("skipping download, file exists:", local_filename)
        r.close()
        return local_filename

    text = r.text
    r.close()
    return text


