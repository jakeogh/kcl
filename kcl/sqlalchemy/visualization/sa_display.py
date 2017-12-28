#!/usr/bin/env python3

import click
import sadisplay
import codecs
import time
import pydot
import os

from PIL import Image

def sa_display(remote_globals):
    desc = sadisplay.describe(remote_globals.values())
    #desc = sadisplay.describe(globals().values())
    dotfile = '/tmp/sadisplay.schema.' + str(time.time()) + '.dot'
    pngfile = '/tmp/sadisplay.schema.' + str(time.time()) + '.dot' + '.png'

    #with codecs.open('schema.plantuml', 'w', encoding='utf-8') as f:
    #    f.write(sadisplay.plantuml(desc))
    #with codecs.open(dotfile, 'w', encoding='utf-8') as f:
    #    f.write(sadisplay.dot(desc))

    #(graph,) = pydot.graph_from_dot_file(dotfile)
    (graph,) = pydot.graph_from_dot_data(sadisplay.dot(desc))
    graph.write_png(pngfile)
    os.system("xdg-open " pngfile)
    #image = Image.open(dotfile + '.png')
    #image.show()
