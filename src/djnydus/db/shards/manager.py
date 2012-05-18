"""
djnydus.shards.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.db.manager import Manager

from .query import PartitionQuerySet


class PartitionManager(Manager):
    """
    Allows operation of partitions by passing key to get_query_set().
    """
    def shard(self, key, slave=False):
        """
        Given a key, which is defined by the partition and used to route queries, returns a QuerySet
        that is bound to the correct shard.

        >>> shard(343)

        >>> shard(343, slave=True)
        """
        queryset = self.get_query_set(key)
        return queryset.using(self.get_database_from_key(key, slave=slave))

    def get_database(self, shard, slave=False):
        """
        Given a shard (numeric index value), returns the correct database alias to query against.

        If ``slave`` is True, returns a read-slave.
        """
        try:
            model = self.model._shards.nodes[shard]
        except IndexError:
            raise ValueError('Shard %r does not exist on %r' % (shard, self.model.__name__))
        return model._shards.get_database(slave=slave)

    def get_database_from_key(self, key, slave=False):
        """
        Given a key, which is defined by the partition and used to route queries, returns the
        database connection alias which the data lives on.
        """
        return self.get_database(key % self.model._shards.num_shards, slave=slave)

    def get_model_from_key(self, key):
        """
        Given a key, which is defined by the partition and used to route queries, returns the
        Model which represents the shard.
        """
        shards = self.model._shards
        return shards.nodes[key % shards.num_shards]

    def get_query_set(self, key=None):
        shards = self.model._shards

        assert key is not None, 'You must filter on %r before expanding a QuerySet on partitioned models.' % (shards.key,)

        model = self.get_model_from_key(key)

        return PartitionQuerySet(model=model, actual_model=self.model)

    def _wrap(func_name):
        def wrapped(self, **kwargs):
            shards = self.model._shards
            key = kwargs.get(shards.key)

            assert key, 'You must pass %r to partitioned models.' % (shards.key,)

            return getattr(self.get_query_set(key=key), func_name)(**kwargs)

        wrapped.__name__ = func_name
        return wrapped

    filter = _wrap('filter')
    get = _wrap('get')
    create = _wrap('create')
    get_or_create = _wrap('get_or_create')
