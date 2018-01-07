#!/usr/bin/env python3

import click
from kcl.sqlalchemy.self_contained_session import self_contained_session
#from kcl.sqlalchemy.model.FileRecord import FileRecord
from kcl.sqlalchemy.BaseMixin import BASE


@click.command()
@click.argument('classname', type=str, nargs=1)
@click.pass_obj
def record(config, classname):
    with self_contained_session(config.database) as session:
        BASE.metadata.create_all(session.bind)
        class_path = '.'.join(classname.split('.')[0:-1])
        classname = classname.split('.')[-1]
        globals()[classname] = __import__(classname, globals=globals(), locals=locals(), fromlist=[classname], level=0)
        cmd_to_eval = classname + ' = ' + class_path + '.' + classname
        print(cmd_to_eval)
        exec(cmd_to_eval)
        #filerecord = FileRecord.construct(session=session, inpath=path)
        import IPython; IPython.embed()
        #session.commit()
        #print(bytes(filerecord))
