#!/usr/bin/env python3

import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import database_exists
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Session, relationship, backref, joinedload_all
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
#from sqlalchemy.types import BINARY
#from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.types import LargeBinary as BINARY
from sqlalchemy.types import Unicode
from sqlalchemy.sql import select
import inspect
import os

def ceprint(*args, **kwargs):
    '''Simple debugging replacement for print()'''
    caller = sys._getframe(1).f_code.co_name
    stack = inspect.stack()
    frm = stack[1]
    depth = len(stack)
    mod = str(inspect.getmodule(frm[0]))
    source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    head = ' '.join([str(depth).zfill(3), str("%.5f" % time.time()), str(os.getpid()), source_file, caller+'()'])
    print('{0: <49}'.format(head),
          *args,
          file=sys.stderr,
          **kwargs)

BASE = declarative_base()

def msg(msg, *args):
    msg = msg % args
    print("\n\n\n" + "-" * len(msg.split("\n")[0]))
    print(msg)
    print("-" * len(msg.split("\n")[0]))

def get_engine(database, echo=False, poolclass=NullPool):
    assert isinstance(database, str)
    engine = create_engine(database, echo=echo, poolclass=poolclass)
    return engine


# https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
@contextlib.contextmanager
def self_contained_session(db_url, echo=False, engine=False):
    if not database_exists(db_url):
        print("creating empty database:", db_url)
        create_database(db_url)
    if not engine:
        engine = create_engine(db_url, poolclass=NullPool, echo=echo)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_session
    # db_session.close() # pylint says: Instance of 'scoped_session' has no 'close' member (no-member)
    # further reading the docs, since db_session is a scoped_session:
    # http://docs.sqlalchemy.org/en/latest/orm/contextual.html
    # The scoped_session.remove() method first calls Session.close() on the current Session,
    # which has the effect of releasing any connection/transactional resources owned by the
    # Session first, then discarding the Session itself. “Releasing” here means that
    # connections are returned to their connection pool and any transactional state is rolled
    # back, ultimately using the rollback() method of the underlying DBAPI connection.
    #
    # so in short, even though its not throwing a runtime error, dont db_session.close()
    # instead call db_session.remove() if using scoped_session
    db_session.remove() # should call Session.close() on its own
    connection.close()
    engine.dispose() # not sure how necessary this is


'''
    storage of filesystem paths via an adjencency list
    http://docs.sqlalchemy.org/en/latest/_modules/examples/adjacency_list/adjacency_list.html
    http://docs.sqlalchemy.org/en/latest/orm/examples.html#examples-adjacencylist

    # how to print SQL before it's executed (dont use str():
    # http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries/
    #from sqlalchemy.dialects import postgresql
    #print str(q.statement.compile(dialect=postgresql.dialect()))

'''


def get_one_or_create(session, model, *args, create_method='', create_method_kwargs=None, **kwargs):
    '''
        Find and return existing ORM object or create and return a new one. Adapted from examples.
    '''
    assert session
    #print('')
    #ceprint("entering get_one_or_create() model:", model, kwargs)
    #for key in kwargs.keys(): # not sure why this was necessary
    #    if issubclass(kwargs[key].__class__, model):
    #        ceprint("returning early with kwargs["+key+"]:", kwargs[key])
    #        return kwargs[key]
    #    ceprint("key:", key)
    #    ceprint("kwargs[key]:", kwargs[key])
    try:
        #ceprint("session.query filter_by:", kwargs)
        result = session.query(model).filter_by(**kwargs).one()
    except NoResultFound as e:
        #ceprint("NoResultFound")
        #import pdb; pdb.set_trace()
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(*args, **kwargs)
        try:
            session.add(created)
            session.flush(objects=[created])
            #ceprint("created.id:", created.id, "type(created):", type(created), "created:", created)
            return created
        except IntegrityError as e:
            #ceprint("IntegrityError:", e, model)
            #ceprint("calling session.rollback()")
            session.rollback() # inklesspen | get_one_or_create() is _sometimes_ going to roll back a transaction

            # catches the race condition assuming the IntegrityError was due to the race hitting a unique constraint
            # in the case where the IntegrityError was caused by something other than a race, like voilating a
            # CheckConstraint("position(' ' in word) = 0") then result will be None
            # if so, it makes sense to re-raise the IntegrityError so the calling code can do something about it.
            try:
                result = session.query(model).filter_by(**kwargs).one()
            except NoResultFound:
                #ceprint("re-raising IntegrityError")
                #import pdb; pdb.set_trace()
                raise e
            return result
    return result


class Filename(BASE):
    __tablename__ = 'filename'
    '''
    UNIX filenames can be anything but NULL and / therefore a binary type is
    required.
    Max file name length is 255 on all UNIX-like filesystems.
    This does not store the path to the filename, so / is not allowed

    Most filesystems do not _have_ a byte encoding, all bytes but NULL are
    valid in a path.
    The user enviroment might interperit the names with a encoding like UTF8,
    but this has no effect on what bytes are possible to store in filenames.

    '''
    id = Column(Integer, primary_key=True)

    #filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0" #todo test
    #filename = Column(BINARY(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)
    #filename = Column(BINARY(255), unique=True, nullable=False, index=True) # sqlite didnt like the constraint
    # Unicode for debugging
    filename = Column(Unicode(255), unique=True, nullable=False, index=True) # sqlite didnt like the constraint

    #def __repr__(self):
    #    return "<Filename(id=%s filename=%s)>" % (str(self.id), str(self.filename))

    def __repr__(self):
        return "Filename(id=%r, filename=%r)" % (
            self.id,
            self.filename
        )

    #def __bytes__(self):
    #    return self.filename


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
        return "Path(filename=%r, id=%r, parent_id=%r, path=%r)" % (
            self.filename,
            self.id,
            self.parent_id,
            self.path
        )

    @hybrid_property
    def path(self):
        if self.parent:
            path = '/'.join([self.parent.path, self.filename.filename])
        else:
            path = self.filename.filename
        return path

    @path.expression
    def path(cls):
        path = select([Path.id]).where(Path.id==cls.parent_id)
        return path

    @classmethod
    def construct(cls, *, session, path):
        #ceprint("path:", path)
        #assert isinstance(path, bytes)
        path_split = path.split('/')
        parent_path = '/'.join(path_split[0:-1])
        filename = path_split[-1]
        filename = get_one_or_create(session, Filename, filename=filename)
        if filename.filename != '':
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
    import sys
    try:
        if sys.argv[1] == 'sqlite':
            database = 'sqlite://'
            engine = create_engine(database, echo=True)
        else:
            print("unknown database engine, exiting")
            quit(1)
    except IndexError:
        database = 'postgresql://postgres@localhost/path_adj_test_' + str(int(time.time()))
        engine = get_engine(database=database, echo=False)


    with self_contained_session(db_url=database, echo=False, engine=engine) as session:
        msg("Creating Tables:")
        BASE.metadata.create_all(engine)

        #msg("Removing all items from the session, selecting path on root, "
        #    "using eager loading to join four levels deep.")
        ## http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html#expunging
        #session.expunge_all()
        ## http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html
        #tree_from_root = session.query(Path).\
        #    options(joinedload_all("children", "children",
        #                           "children", "children")).\
        #    filter(Path.filename == root_filename).\
        #    first()
        #msg("tree_from_root:\n%s", tree_from_root.dump())

        print("attempting construct()")
        new_path = Path.construct(session=session, path='/a')
        session.add(new_path)
        session.commit()
        assert new_path.path == '/a'

        print("attempting construct()")
        new_path = Path.construct(session=session, path='/b')
        session.add(new_path)
        session.commit()
        assert new_path.path == '/b'

        print("attempting construct()")
        new_path = Path.construct(session=session, path='/a/c')
        session.add(new_path)
        session.commit()
        assert new_path.path == '/a/c'

        root_path = Path.construct(session=session, path='/')

        from IPython import embed; embed()
        #msg("root_path:\n%s", root_path.dump())

