#!/usr/bin/env python3

import click
from icecream import ic
from kcl.htmlops import extract_iris_from_text_file
from kcl.htmlops import extract_iris_from_text
from kcl.inputops import enumerate_input
from kcl.printops import ceprint


@click.command()
@click.argument('paths', type=str, nargs=-1, required=False)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--notpaths', is_flag=True)
@click.option('--null', is_flag=True)
@click.pass_obj
def _text(config,
          paths,
          notpaths,
          null,
          verbose,
          debug):

    for index, path in enumerate_input(iterator=paths,
                                       null=null,
                                       debug=debug,
                                       verbose=verbose):
        if verbose:
            ic(index, path)

        if verbose:
            ceprint("path:", path)
        if notpaths:
            urls = extract_iris_from_text(path)
        else:
            urls = extract_iris_from_text_file(path)

        for url in urls:
            print(url)
