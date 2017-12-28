#!/usr/bin/env python3

import click
import sadisplay
import codecs
import time
import pydot

def sa_display(remote_globals):
    desc = sadisplay.describe(remote_globals().values())
    #desc = sadisplay.describe(globals().values())
    dotfile = 'sadisplay.schema.' + str(time.time()) + '.dot'

    #with codecs.open('schema.plantuml', 'w', encoding='utf-8') as f:
    #    f.write(sadisplay.plantuml(desc))
    with codecs.open(dotfile, 'w', encoding='utf-8') as f:
        f.write(sadisplay.dot(desc))

    (graph,) = pydot.graph_from_dot_file(dotfile)
    graph.write_png(dotfile + '.png')

