#!/usr/bin/env python3

import click
from kcl.sqlalchemy.self_contained_session import self_contained_session
#from kcl.sqlalchemy.model.FileRecord import FileRecord
from kcl.sqlalchemy.BaseMixin import BASE


@click.command()
@click.argument('class_name', type=str, nargs=1)
@click.pass_obj
def record(config, class_name):
    with self_contained_session(config.database) as session:
        BASE.metadata.create_all(session.bind)
        class_path = '.'.join(class_name.split('.')[0:-1])
        class_name = class_name.split('.')[-1]
        full_class_path = class_path + '.' + class_name
        #globals()[class_name] = __import__(full_class_path, globals=globals(), locals=locals(), fromlist=[class_name], level=0)
        globals()[class_name] = getattr(__import__(full_class_path, globals=globals(), locals=locals(), fromlist=[class_name], level=0), class_name)
        #cmd_to_eval = class_name + ' = ' + class_name + '.' + class_name
        #print(cmd_to_eval)
        #exec(cmd_to_eval)

        #class_name = getattr(class_name, class_name)
        import IPython; IPython.embed()
        #session.commit()
        #print(bytes(filerecord))
