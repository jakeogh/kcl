#!/usr/bin/env python3

import click
from kcl.htmlops import extract_urls_lxml
from kcl.printops import ceprint

@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, path_type=bytes, allow_dash=False, resolve_path=False), nargs=1, required=True)
@click.argument('iri', type=str, nargs=1, required=True)
@click.option('--link-text', is_flag=True)
@click.option('--verbose', is_flag=True)
@click.pass_obj
def _lxml(config, path, iri, link_text, verbose):
    if verbose:
        ceprint("path:", path)
        ceprint("iri:", iri)
    urls = extract_urls_lxml(html_file=path, uri=iri, link_text=link_text)
    for url in urls:
        if link_text:
            print(url[0], url[1])
        else:
            print(url)
