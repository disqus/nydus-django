"""
djnydus.shards.query
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import router, transaction
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError

_queryset_registry = {}


class OptionsProxy(object):
    def __init__(self, modelproxy):
        self._modelproxy = modelproxy
        self._options = modelproxy._model._meta

    def __getattr__(self, name):
        return getattr(self._options, name)

    def __setattr__(self, name, value):
        return setattr(self._options, name, value)

    @property
    def db_table(self):
        return self._modelproxy.db_table


class ModelProxy(object):
    def __init__(self, model):
        self._model = model
        self.db_table = None

    def __getattr__(self, name):
        if name == '_meta':
            if not hasattr(self, '_meta'):
                self._meta = OptionsProxy(self)
            return OptionsProxy(self)
        return getattr(self._model, name)

    def __setattr__(self, name, value):
        return setattr(self._model, name, value)


class PartitionQuerySetBase(object):
    @property
    def db(self):
        if self._db:
            return self._db

        if self._for_write:
            return router.db_for_write(self.model, instance=getattr(self, '_instance', None))
        return router.db_for_read(self.model)

    def _filter_or_exclude(self, *args, **kwargs):
        clone = super(PartitionQuerySet, self)._filter_or_exclude(*args, **kwargs)
        if getattr(clone, '_exact_lookups', None) is None:
            clone._exact_lookups = {}
        clone._exact_lookups.update(dict([(k, v) for k, v in kwargs.items() if '__' not in k]))
        return clone

    def _clone(self, klass=None, *args, **kwargs):
        if klass is not QuerySet:
            if klass not in _queryset_registry:
                _queryset_registry[klass] = partition_query_set_factory(klass)
            klass = _queryset_registry[klass]

        clone = super(PartitionQuerySet, self)._clone(klass, *args, **kwargs)
        clone._exact_lookups = self._exact_lookups.copy()
        return clone

    def iterator(self):
        assert self.model.db_table, "You must filter on a routing key before performing additional operations" \
            " on this queryset."

        return super(PartitionQuerySet, self).iterator()


class PartitionQuerySet(PartitionQuerySetBase, QuerySet):
    """
    QuerySet which helps partitioning by field in the database routers by
    providing hints about what fields are being queried against.
    """
    def __init__(self, model, *args, **kwargs):
        self._exact_lookups = {}
        model = ModelProxy(model)
        super(PartitionQuerySet, self).__init__(model, *args, **kwargs)

    def create(self, **kwargs):
        """
        This is a copy of QuerySet.create, except we save the instance we're
        about to save for the db_for_write router.  This can't use super()
        since we'll either be too early (before the instance is created) or
        too late (after the ``db`` property is hit).
        """
        obj = self.model(**kwargs)
        self._for_write = True
        self._instance = obj
        obj.save(force_insert=True, using=self.db)
        return obj

    def get_or_create(self, **kwargs):
        """
        This is a copy of QuerySet.get_or_create, that forces calling our custom
        create method when the get fails.
        """
        assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        try:
            self._for_write = True
            return self.get(**kwargs), False
        except ObjectDoesNotExist:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            obj = self.model(**params)
            self._for_write = True
            self._instance = obj
            using = self.db
            try:
                sid = transaction.savepoint(using=using)
                obj.save(force_insert=True, using=using)
            except IntegrityError:
                transaction.savepoint_rollback(sid, using=using)
                return self.get(**kwargs), False
            else:
                transaction.savepoint_commit(sid, using=using)
                return obj, True


def partition_query_set_factory(klass):
    class _PartitionQuerySetFromFactory(PartitionQuerySetBase, klass):
        def _clone(self, klass=None, *args, **kwargs):
            clone = super(_PartitionQuerySetFromFactory, self)._clone(klass, *args, **kwargs)
            clone._exact_lookups = self._exact_lookups.copy()
            return clone

    return _PartitionQuerySetFromFactory
