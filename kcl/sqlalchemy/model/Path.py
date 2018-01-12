#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, create_engine
from sqlalchemy import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Session, relationship, backref, joinedload_all
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
#from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.types import BINARY
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
BASE = declarative_base()


def get_one_or_create(session, model, *args, create_method='', create_method_kwargs=None, **kwargs):
    '''Find and return existing ORM object or create and return a new one. Adapted from examples.'''
    assert session
    for key in kwargs.keys():
        if issubclass(kwargs[key].__class__, model):
            print("returning early")
            return kwargs[key]
    try:
        print("session.query filter_by:", kwargs)
        result = session.query(model).filter_by(**kwargs).one()
    except NoResultFound as e:
        print("NoResultFound")
        #import pdb; pdb.set_trace()
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(*args, **kwargs)
        try:
            session.add(created)
            session.flush(objects=[created])
            print("ret:", created.id, created)
            return created
        except IntegrityError as e:
            print("IntegrityError:", e, model)
            print("calling session.rollback()")
            session.rollback() # inklesspen | get_one_or_create() is _sometimes_ going to roll back a transaction

            # catches the race condition assuming the IntegrityError was due to the race hitting a unique constraint
            # in the case where the IntegrityError was caused by something other than a race, like voilating a
            # CheckConstraint("position(' ' in word) = 0") then result will be None
            # if so, it makes sense to re-raise the IntegrityError so the calling code can do something about it.
            try:
                result = session.query(model).filter_by(**kwargs).one()
            except NoResultFound:
                print("re-raising IntegrityError")
                #import pdb; pdb.set_trace()
                raise e
            return result
    return result


class Filename(BASE):
    __tablename__ = 'filename'
    '''
    UNIX filenames can be anything but NULL and / therefore a binary type is required.
    max file name length is 255 on all UNIX-like filesystems
    this does not store the path to the filename, so / is not allowed

    Most filesystems do not _have_ a byte encoding, all bytes but NULL are valid in a path.
    The user enviroment might interperit the names with a encoding like UTF8, but this has
    no effect on what bytes are possible to store in filenames.

    '''
    id = Column(Integer, primary_key=True)

    #filename_constraint = "position('\\x00' in filename) = 0 and position('\\x2f' in filename) = 0" #todo test
    #filename = Column(BINARY(255), CheckConstraint(filename_constraint), unique=True, nullable=False, index=True)
    filename = Column(BINARY(255), unique=True, nullable=False, index=True) # sqlite didnt like the constraint

    def __repr__(self):
        return "<Filename(id=%s filename=%s)>" % (str(self.id), str(self.filename))

    def __bytes__(self):
        return self.filename


class Path(BASE):
    '''
        adjacency list example modified to model a filesystem
        https://github.com/zzzeek/sqlalchemy/blob/master/examples/adjacency_list/adjacency_list.py
    '''

    __tablename__ = 'path'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(id))
    #filename = Column(String(50), nullable=True, unique=True)

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
        collection_class=attribute_mapped_collection('filename'),
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
            return b'/'.join([self.parent.path, bytes(self.filename)])
        return bytes(self.filename)

    @path.expression
    def path(cls):
        if cls.parent:
            return cls.parent.path + b'/' + cls.filename.filename
        return cls.filename.filename

    @classmethod
    def construct(cls, *, session, path):
        assert isinstance(path, bytes)
        path_split = path.split(b'/')
        parent_path = b'/'.join(path_split[0:-1])
        filename = path_split[-1]
        filename = get_one_or_create(session, Filename, filename=filename)
        parent = get_one_or_create(session=session,
                                   model=Path,
                                   path=parent_path,  # searching the hybrid_property
                                   create_method='construct',
                                   create_method_kwargs={'path':parent_path, 'session':session})

        new_path = get_one_or_create(session, Path, parent=parent, filename=filename)
        return new_path

    def dump(self, _indent=0):
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c.dump(_indent + 1)
                for c in self.children.values()
            ])


if __name__ == '__main__':
    engine = create_engine('sqlite://', echo=True)

    def msg(msg, *args):
        msg = msg % args
        print("\n\n\n" + "-" * len(msg.split("\n")[0]))
        print(msg)
        print("-" * len(msg.split("\n")[0]))

    msg("Creating Tables:")
    BASE.metadata.create_all(engine)
    session = Session(engine)

    root_filename = Filename(filename=b'')
    root_path = Path(filename=root_filename)
    session.add(root_path)
    session.commit()
    print("tmp_path:", root_path, '\n\n')

    tmp_filename = Filename(filename=b'tmp')
    tmp_path = Path(parent=root_path, filename=tmp_filename)
    session.add(tmp_path)
    session.commit()
    print("tmp_path:", tmp_path, '\n\n')

    msg("Emptying out the session entirely, selecting path on root, using "
        "eager loading to join four levels deep.")
    session.expunge_all()
    node = session.query(Path).\
        options(joinedload_all("children", "children",
                               "children", "children")).\
        filter(Path.filename == root_filename).\
        first()

    msg("Full Path:\n%s", node.dump())

    print("attempting construct()")
    newpath = Path.construct(session=session, path=b'/var')




    #node = Path('')
    #Path('node1', parent=node)
    #Path('node3', parent=node)

    #node2 = Path('node2')
    #Path('subnode1', parent=node2)
    #node.children['node2'] = node2
    #Path('subnode2', parent=node.children['node2'])

    #msg("Created new path structure:\n%s", node.dump())

    #msg("flush + commit:")

    #session.add(node)
    #session.commit()

    #msg("Path After Save:\n %s", node.dump())

    #Path('node4', parent=node)
    #Path('subnode3', parent=node.children['node4'])
    #Path('subnode4', parent=node.children['node4'])
    #Path('subsubnode1', parent=node.children['node4'].children['subnode3'])
    #sub = Path('jsubsubnode2', parent=node.children['node4'].children['subnode3'].children['subsubnode1'])
    #subsub = Path('jksubsubnode2', parent=sub)

    ## remove node1 from the parent, which will trigger a delete
    ## via the delete-orphan cascade.
    #del node.children['node1']

    #msg("Removed node1.  flush + commit:")
    #session.commit()

    #msg("Path after save:\n %s", node.dump())

    #msg("Emptying out the session entirely, selecting path on root, using "
    #    "eager loading to join four levels deep.")
    #session.expunge_all()
    #node = session.query(Path).\
    #    options(joinedload_all("children", "children",
    #                           "children", "children")).\
    #    filter(Path.filename == "").\
    #    first()

    #msg("Full Path:\n%s", node.dump())

    #msg("Marking root node as deleted, flush + commit:")

    #session.delete(node)
    #session.commit()
