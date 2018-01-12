#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, relationship, backref, joinedload_all
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from kcl.sqlalchemy.BaseMixin import BASE
from .Filename import Filename


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

    def __init__(self, **kwargs):
        if 'path' in kwargs.keys():
            path_split = kwargs['path']
            parent_path = b'/'.join(path_split[0:-1])
            parent = get_one_or_create(self.) #hmph, need session


    @hybrid_property
    def path(self):
        if self.parent:
            return '/'.join([self.parent.path, self.filename])
        return self.filename

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

    msg("Creating Path Table:")

    BASE.metadata.create_all(engine)

    session = Session(engine)

    node = Path('')
    Path('node1', parent=node)
    Path('node3', parent=node)

    node2 = Path('node2')
    Path('subnode1', parent=node2)
    node.children['node2'] = node2
    Path('subnode2', parent=node.children['node2'])

    msg("Created new path structure:\n%s", node.dump())

    msg("flush + commit:")

    session.add(node)
    session.commit()

    msg("Path After Save:\n %s", node.dump())

    Path('node4', parent=node)
    Path('subnode3', parent=node.children['node4'])
    Path('subnode4', parent=node.children['node4'])
    Path('subsubnode1', parent=node.children['node4'].children['subnode3'])
    sub = Path('jsubsubnode2', parent=node.children['node4'].children['subnode3'].children['subsubnode1'])
    subsub = Path('jksubsubnode2', parent=sub)

    # remove node1 from the parent, which will trigger a delete
    # via the delete-orphan cascade.
    del node.children['node1']

    msg("Removed node1.  flush + commit:")
    session.commit()

    msg("Path after save:\n %s", node.dump())

    msg("Emptying out the session entirely, selecting path on root, using "
        "eager loading to join four levels deep.")
    session.expunge_all()
    node = session.query(Path).\
        options(joinedload_all("children", "children",
                               "children", "children")).\
        filter(Path.filename == "").\
        first()

    msg("Full Path:\n%s", node.dump())

    msg("Marking root node as deleted, flush + commit:")

    session.delete(node)
    session.commit()
