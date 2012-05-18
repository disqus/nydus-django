"""
djnydus.shards.options
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.db import connections
from threading import local

from .utils import get_cluster_sizes

CLUSTER_SIZES = get_cluster_sizes(connections)
DEFAULT_NAMES = ('num_shards', 'key', 'sequence', 'abstract', 'cluster')


class ShardInfo(object):
    def __init__(self, options, nodes=[]):
        self.options = options
        self.nodes = nodes
        self.model = None
        self.name = None
        self.size = None

    def __repr__(self):
        return u'<%s: model=%s, options=%s, nodes=%s>' % (
            self.__class__.__name__, self.model,
            self.options, len(self.nodes))

    @property
    def is_child(self):
        return False

    @property
    def is_master(self):
        return True

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls
        setattr(cls, name, self)

        opts = self.options

        if opts:
            for k in (k for k in DEFAULT_NAMES if hasattr(opts, k)):
                setattr(self, k, getattr(opts, k))

        if not hasattr(self, 'sequence'):
            self.sequence = cls._meta.db_table

        if hasattr(self, 'cluster'):
            self.size = CLUSTER_SIZES[self.cluster]

    # def get_all_databases(self):
    #     """
    #     Returns a list of all database aliases that this shard is
    #     bound to.
    #     """
    #     return (self.get_database(), self.get_database(slave=True))

    # def get_database(self, slave=False):
    #     parent = self.parent._shards
    #     alias = parent.cluster
    #     if slave:
    #         alias += '.slave'
    #     alias += '.shard%d' % (self.num % parent.size,)
    #     return alias


class ShardOptions(local):
    def __init__(self, options):
        self._opts = options
        self.db_table = None

    def __getattr__(self, name):
        return getattr(self._opts, name)

    def __setattr__(self, name, value):
        return setattr(self._opts, name, value)
