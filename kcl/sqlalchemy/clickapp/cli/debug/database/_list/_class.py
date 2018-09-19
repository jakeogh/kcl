#!/usr/bin/env python3

import click
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.model.BaseMixin import BASE
from kcl.cli.CONTEXT_SETTINGS import CONTEXT_SETTINGS
CONTEXT_SETTINGS['ignore_unknown_options'] = True
CONTEXT_SETTINGS['allow_extra_args'] = True


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('class_name', type=str, nargs=1)
@click.pass_context
def _class(ctx, class_name):
    with self_contained_session(ctx.obj.database) as session:
        BASE.metadata.create_all(session.bind)
        class_path = '.'.join(class_name.split('.')[0:-1])
        class_name = class_name.split('.')[-1]
        full_class_path = class_path + '.' + class_name
        globals()[class_name] = getattr(__import__(full_class_path, globals=globals(), locals=locals(), fromlist=[class_name], level=0), class_name)
        object_generator = session.query(globals()[class_name])
        for obj in object_generator:
            print(obj)
