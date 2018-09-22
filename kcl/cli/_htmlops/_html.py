#!/usr/bin/env python3

import click
from kcl.htmlops import extract_iris_from_html_file
from kcl.printops import ceprint

@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, path_type=bytes, allow_dash=False, resolve_path=False), nargs=1, required=True)
@click.option('--verbose', is_flag=True)
@click.pass_obj
def _html(config, path, verbose):
    if verbose:
        ceprint("path:", path)
    urls = extract_iris_from_html_file(path)
    for url in urls:
        print(url)
