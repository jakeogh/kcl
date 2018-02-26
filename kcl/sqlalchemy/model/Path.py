#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer
#from sqlalchemy import func
#from sqlalchemy import CheckConstraint
#from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
#from sqlalchemy.orm import joinedload_all
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
#from sqlalchemy.types import BINARY
#from sqlalchemy.dialects.postgresql import BYTEA
#from sqlalchemy.types import LargeBinary as BINARY
#from sqlalchemy.types import Unicode
from sqlalchemy.sql import select
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

    @hybrid_property
    def path(self):
        if self.parent:
            path = b'/'.join([self.parent.path, self.filename.filename])
        else:
            path = self.filename.filename
        return path

    @path.expression
    def path(cls):
        path = select([Path.id]).where(Path.id==cls.parent_id)
        return path

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
                                       model=Path,
                                       path=parent_path,  # searching the hybrid_property
                                       create_method='construct',
                                       create_method_kwargs={'path':parent_path, 'session':session})
            session.commit()
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

        print("attempting construct()")
        new_path = Path.construct(session=session, path=b'/a')
        session.add(new_path)
        session.commit()
        assert new_path.path == b'/a'

        print("attempting construct()")
        new_path = Path.construct(session=session, path=b'/b')
        session.add(new_path)
        session.commit()
        assert new_path.path == b'/b'

        print("attempting construct()")
        new_path = Path.construct(session=session, path=b'/a/c/d/e/f/g')
        session.add(new_path)
        session.commit()
        assert new_path.path == b'/a/c/d/e/f/g'

        print("attempting construct()")
        new_path = Path.construct(session=session, path=b'/a/c')
        session.add(new_path)
        session.commit()
        assert new_path.path == b'/a/c'

        root_path = Path.construct(session=session, path=b'/')

        #from IPython import embed; embed()
        msg("root_path:\n%s", root_path.dump())
