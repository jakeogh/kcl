#!/usr/bin/env python3

import click
from getdents import paths
from kcl.printops import ceprint
#from kcl.printops import eprint
#from getdents import DentGen

@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False, allow_dash=False, resolve_path=False), nargs=1, required=True)
@click.option('--verbose', is_flag=True)
@click.pass_obj
def _iterate(config, path, verbose):
    if verbose:
        ceprint("path:", path)
    for item in paths(path):
        print(item)
    #dentgen = DentGen(path).go()
    #for item in dentgen:
    #    print(item)
