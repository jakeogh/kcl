#!/usr/bin/env python3

import click
from kcl.redisops import get_keys
from kcl.redisops import get_size_of_key
from kcl.printops import ceprint


@click.command()
@click.argument('pattern', type=str, nargs=1, required=False)
@click.option('--type', is_flag=True)
@click.option('--size', is_flag=True)
@click.option('--verbose', is_flag=True)
@click.pass_obj
def _keys(config, pattern, iri, link_text, verbose):
    if verbose:
        ceprint("pattern:", pattern)
    for key in get_keys(pattern=pattern):
        print(key)
