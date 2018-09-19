#!/usr/bin/env python3

import click
from kcl.htmlops import extract_urls_lxml


@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, path_type=bytes, allow_dash=False, resolve_path=False), nargs=1, required=True)
@click.argument('iri', type=str, nargs=1, required=True)
@click.option('--verbose', is_flag=True)
@click.pass_obj
def _lxml(config, path, iri, verbose):
    urls = extract_urls_lxml(path, iri)
    for url in urls:
        print(url)
