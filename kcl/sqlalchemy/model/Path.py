#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from kcl.printops import ceprint
from kcl.sqlalchemy.model.BaseMixin import BASE
from kcl.sqlalchemy.model.Filename import Filename
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.get_one_or_create import get_one_or_create

'''
    storage of filesystem paths via an adjencency list
    http://docs.sqlalchemy.org/en/latest/_modules/examples/adjacency_list/adjacency_list.html
    http://docs.sqlalchemy.org/en/latest/orm/examples.html#examples-adjacencylist

    # how to print SQL before it's executed (dont use str():
    # http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries/
    #from sqlalchemy.dialects import postgresql
    #print str(q.statement.compile(dialect=postgresql.dialect()))

'''


def msg(msg, *args):
    msg = msg % args
    print("\n\n\n" + "-" * len(msg.split("\n")[0]))
    print(msg)
    print("-" * len(msg.split("\n")[0]))


class Path(BASE):
    '''
        adjacency list example modified to model a filesystem
        https://github.com/zzzeek/sqlalchemy/blob/master/examples/adjacency_list/adjacency_list.py
    '''

    __tablename__ = 'path'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(id))
    children = relationship(
        "Path",
        # cascade deletions
        cascade="all, delete-orphan",

        # many to one + adjacency list - remote_side
        # is required to reference the 'remote'
        # column in the join condition.
        backref=backref("parent", remote_side=id),

        # children will be represented as a dictionary
        # on the "filename" attribute.
        collection_class=attribute_mapped_collection('filename')
    )

    filename_id = Column(Integer, ForeignKey("filename.id"), unique=False, nullable=False)
    filename = relationship("Filename", backref='paths')

    def __init__(self, filename, parent=None):
        self.filename = filename
        self.parent = parent

    def __repr__(self):
        return "Path(id=%r, parent_id=%r, path=%r)" % (
            self.id,
            self.parent_id,
            self.path
        )

    ##@hybrid_property
    #@property
    #def path(self):
    #    ceprint('@hybrid_property')
    #    #return self.path
    #    if self.parent:
    #        path = b'/'.join([self.parent.path, self.filename.filename])
    #    else:
    #        path = self.filename.filename
    #    return path

    #@path.expression
    @property
    def path(cls):
        ceprint('@path.expression')
        #path = select([Path.id]).where(Path.id==cls.parent_id)
        path = "WITH RECURSIVE parents AS (SELECT id, parent_id, filename_id FROM path WHERE id = path.id UNION SELECT path.id, path.parent_id, path.filename_id FROM path INNER JOIN parents ON parents.parent_id = path.id) SELECT string_agg(filename      , '/' ORDER BY parent_id NULLS FIRST) FROM parents JOIN filename ON filename.id = parents.filename_id;"
        print(path)
        #path = "WITH RECURSIVE parents AS (SELECT id, parent_id, filename_id FROM path WHERE id = 7 UNION SELECT path.id, path.parent_id, path.filename_id FROM path INNER JOIN parents ON parents.parent_id = path.id) SELECT string_agg(filename      , '/' ORDER BY parent_id NULLS FIRST) FROM parents JOIN filename ON filename.id = parents.filename_id;"
        return path

        # r = session.execute("WITH RECURSIVE parents AS (SELECT id, parent_id, filename_id FROM path WHERE id = 7 UNION SELECT path.id, path.parent_id, path.filename_id FROM path INNER JOIN parents ON parents.parent_id = path.id) SELECT string_agg(filename, '/' ORDER BY parent_id NULLS FIRST) FROM parents JOIN filename ON filename.id = parents.filename_id;").scalar(); bytes(r)


    @classmethod
    def construct(cls, *, session, path, verbose=False):
        if verbose:
            ceprint(path)
        assert isinstance(path, bytes)
        path_split = path.split(b'/')
        parent_path = b'/'.join(path_split[0:-1])
        filename = path_split[-1]
        filename = get_one_or_create(session, Filename, filename=filename)
        if filename.filename != b'':
            #ceprint("looking for parent_path:", parent_path)
            parent = get_one_or_create(session=session,
                                       verbose=verbose,
                                       model=Path,
                                       path=parent_path,  # searching the hybrid_property
                                       create_method='construct',
                                       create_method_kwargs={'path':parent_path, 'session':session})
            #session.commit()
            assert parent
        else:
            parent = None

        #from IPython import embed; embed()
        new_path = get_one_or_create(session, Path, parent=parent, filename=filename)
        session.commit()
        return new_path

    def dump(self, _indent=0):
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c.dump(_indent + 1)
                for c in self.children.values()
            ])


if __name__ == '__main__':
    import time
    database = 'postgresql://postgres@localhost/path_test_' + str(int(time.time()))

    with self_contained_session(db_url=database, echo=False) as session:
        msg("Creating Tables:")
        BASE.metadata.create_all(session.bind)

#        print("attempting construct()")
#        new_path = Path.construct(session=session, path=b'/a')
#        session.add(new_path)
#        session.commit()
#        assert new_path.path == b'/a'
#
#        print("attempting construct()")
#        new_path = Path.construct(session=session, path=b'/b')
#        session.add(new_path)
#        session.commit()
#        assert new_path.path == b'/b'

        print("attempting construct()")
        new_path = Path.construct(session=session, path=b'/a/c/d/e/f/g')
        session.add(new_path)
        session.commit()
        assert new_path.path == b'/a/c/d/e/f/g'
        print(new_path)

#        print("attempting construct()")
#        new_path = Path.construct(session=session, path=b'/a/c')
#        session.add(new_path)
#        session.commit()
#        assert new_path.path == b'/a/c'
#
#        root_path = Path.construct(session=session, path=b'/')
#
#        #from IPython import embed; embed()
#        msg("root_path:\n%s", root_path.dump())

    # r = session.execute('WITH RECURSIVE parents AS (SELECT id, parent_id, filename_id FROM path WHERE id = 7 UNION SELECT path.id, path.parent_id, path.filename_id FROM path INNER JOIN parents ON parents.parent_id = path.id) SELECT * FROM parents JOIN filename ON filename.id = parents.filename_id ORDER BY CASE WHEN parent_id IS NULL THEN 0 ELSE 1 END, parent_id;').fetchall(); ans = b'/'.join([ bytes(item[-1]) for item in r ])


    # decendents:
    # session.execute('WITH RECURSIVE decendents AS ( SELECT id, parent_id, filename_id FROM path WHERE id = 12 UNION SELECT e.id, e.parent_id, e.filename_id FROM path e INNER JOIN decendents s ON s.id = e.parent_id) SELECT * FROM decendents;').fetchall()

    # session.execute('WITH RECURSIVE parents AS (SELECT id, parent_id, filename_id FROM path WHERE id = 12 UNION SELECT e.id, e.parent_id, e.filename_id FROM path e INNER JOIN parents s ON s.parent_id = e.id) SELECT * FROM parents;').fetchall()
