"""
djnydus.shards.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.db.models.base import ModelBase, Model
from django.db.models.options import Options

from .manager import PartitionManager
from .options import ShardInfo, ShardOptions, DEFAULT_NAMES


class PartitionBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        if 'Meta' not in attrs:
            attrs['Meta'] = type('Meta', (object,), {
                'abstract': True,
            })
        else:
            attrs['Meta'].abstract = True

        if 'objects' not in attrs:
            attrs['objects'] = PartitionManager()

        attrs['Meta'].managed = True

        new_cls = super(PartitionBase, cls).__new__(cls, name, bases, attrs)

        attr_shardopts = attrs.pop('Shards', None)

        if not attr_shardopts:
            shardopts = getattr(new_cls, 'Shards', None)
        else:
            shardopts = attr_shardopts
        base_shardopts = getattr(new_cls, '_shards', None)

        shards = []
        new_cls.add_to_class('_shards', ShardInfo(shardopts, nodes=shards))

        if base_shardopts:
            for k in DEFAULT_NAMES:
                if not hasattr(new_cls._shards, k):
                    setattr(new_cls._shards, k, getattr(base_shardopts, k, None))

        return new_cls

    def add_to_class(cls, name, value):
        if isinstance(value, Options):
            value = ShardOptions(value)
        return super(PartitionBase, cls).add_to_class(name, value)


class PartitionModel(Model):
    __metaclass__ = PartitionBase

    class Meta:
        abstract = True
