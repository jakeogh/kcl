#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

'''
# http://docs.sqlalchemy.org/en/latest/core/engines.html

                    DIALECT
                    /    \
connect() <-> ENGINE      DBAPI <-> DATABASE
                    \    /
                     POOL

# The Engine, once created, can either be used directly to interact with the
# database, or can be passed to a Session object to work with the ORM.

# database URL: dialect+driver://username:password@host:port/database

create_engine()

echo=False – if True, the Engine will log all statements as well as a repr()
             of their parameter lists to the engines logger, which defaults to
             sys.stdout.

echo_pool=False – if True, the connection pool will log all checkouts/checkins
                  to the logging stream, which defaults to sys.stdout.

pool=None – an already-constructed instance of Pool, such as a QueuePool
            instance. If non-None, this pool will be used directly as the
            underlying connection pool for the engine, bypassing whatever
            connection parameters are present in the URL argument. For
            information on constructing connection pools manually, see
            Connection Pooling.

convert_unicode=False – if set to True, sets the default behavior of
                        convert_unicode on the String type to True, regardless
                        of a setting of False on an individual String type,
                        thus causing all String-based columns to accommodate
                        Python unicode objects.

poolclass=None – a Pool subclass, which will be used to create a connection
                 pool instance using the connection parameters given in the
                 URL. Note this differs from pool in that you don’t actually
                 instantiate the pool in this case, you just indicate what type
                 of pool to be used.

    NullPool(sqlalchemy.pool.Pool):

        A Pool which does not pool connections.

        Instead it literally opens and closes the underlying DB-API connection
        per each connection open/close.

        Reconnect-related functions such as recycle and connection invalidation
        are not supported by this Pool implementation, since no connections are
        held persistently.

    StaticPool(sqlalchemy.pool.Pool):

        A Pool of exactly one connection, used for all requests.

        Reconnect-related functions such as recycle and connection invalidation
        (which is also used to support auto-reconnect) are not currently
        supported by this Pool implementation but may be implemented in a
        future release.

    QueuePool(sqlalchemy.pool.Pool):

        A Pool that imposes a limit on the number of open connections.

        QueuePool is the default pooling implementation used for all Engine
        objects, unless the SQLite dialect is in use.

        __init__(creator, pool_size=5, max_overflow=10, timeout=30, **kw)

        creator – a callable function that returns a DB-API connection object,
                  same as that of Pool.creator.

        pool_size – The size of the pool to be maintained, defaults to 5. This
                    is the largest number of connections that will be kept
                    persistently in the pool. Note that the pool begins with no
                    connections; once this number of connections is requested,
                    that number of connections will remain. pool_size can be
                    set to 0 to indicate no size limit; to disable pooling,
                    use a NullPool instead.

        max_overflow – The maximum overflow size of the pool. When the number
                       of checked-out connections reaches the size set in
                       pool_size, additional connections will be returned up to
                       this limit. When those additional connections are
                       returned to the pool, they are disconnected and
                       discarded. It follows then that the total number of
                       simultaneous connections the pool will allow is
                       pool_size + max_overflow, and the total number of
                       “sleeping” connections the pool will allow is pool_size.
                       max_overflow can be set to -1 to indicate no overflow
                       limit; no limit will be placed on the total number of
                       concurrent connections. Defaults to 10.

        timeout – The number of seconds to wait before giving up on returning a
                  connection. Defaults to 30.

        **kw – Other keyword arguments including Pool.recycle, Pool.echo,
               Pool.reset_on_return and others are passed to the Pool
               constructor.
'''

def get_engine(database, echo=False, poolclass=NullPool):
    assert isinstance(database, str)
    engine = create_engine(database, echo=echo, poolclass=poolclass)
    return engine


