"""
djnydus.shards.fields
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.db import connections, transaction
from django.db.models.fields import BigIntegerField
from django.db.models.signals import post_syncdb, class_prepared
from django.db.utils import DatabaseError
from django.utils.translation import ugettext_lazy as _


class SequenceField(BigIntegerField):
    """
    A ``BigIntegerField`` that increments using an external PostgreSQL sequence
    generator.  Used for primary keys on partitioned tables that require a
    canonical source for unique IDs.

        ``db_alias`` is the alias to the Django connection to the database
        containing the sequence.

        ``sequence`` is the string representation of the sequence table.

    """

    description = _("Integer")

    def __init__(self, db_alias, sequence=None, *args, **kwargs):
        self.db_alias = db_alias
        self.sequence = sequence

        kwargs['blank'] = True
        kwargs['editable'] = False
        kwargs['unique'] = True
        super(SequenceField, self).__init__(*args, **kwargs)

    def set_sequence_name(self, **kwargs):
        self._sequence = self.sequence or '%s_%s_seq' % (self.model._meta.db_table, self.column)

    def create_sequence(self, created_models, **kwargs):
        if self.model not in created_models:
            return

        if not getattr(self, '_sequence', None):
            return

        # if hasattr(self.model, '_shards') and hasattr(self.model._shards, 'parent') and self.model._shards.parent not in created_models:
        #     return

        cursor = connections[self.db_alias].cursor()
        sid = transaction.savepoint(self.db_alias)
        try:
            cursor.execute("CREATE SEQUENCE %s;" % self._sequence)
        except DatabaseError:
            transaction.savepoint_rollback(sid, using=self.db_alias)
            # Sequence must already exist, ensure it gets reset
            cursor.execute("SELECT setval('%s', 1, false)" % (self._sequence,))
        else:
            print 'Created sequence %r on %r' % (self._sequence, self.db_alias)
            transaction.savepoint_commit(sid, using=self.db_alias)
        cursor.close()

    def contribute_to_class(self, cls, name):
        super(SequenceField, self).contribute_to_class(cls, name)
        # parent models still call this method, but dont need sequences
        post_syncdb.connect(self.create_sequence)
        class_prepared.connect(self.set_sequence_name, sender=cls)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if add and not value:
            value = self.get_next_value()
            setattr(model_instance, self.attname, value)
        return value

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.PositiveIntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def get_next_value(self):
        cursor = connections[self.db_alias].cursor()
        try:
            cursor.execute("SELECT NEXTVAL(%s)", (self._sequence,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()


class PartitionSequenceField(SequenceField):
    """
    The same as AutoSequenceField except that the sequence is based on the master
    table's default name.

    The behavior of this is slightly odd, as it has to work around the fact that
    the master tables arent actually sync'd, so instead it listens for its first
    child, and attempts to create sequences on creation of that table.
    """
    def set_sequence_name(self, **kwargs):
        if not (hasattr(self.model, '_shards') and self.model._shards.is_master):
            return
        self._sequence = self.sequence or '%s_%s_seq' % (self.model._shards.sequence, self.column)

    def create_sequence(self, created_models, **kwargs):
        # XXX: the parent model never gets called on here from signals due to it not actually
        # being a real table
        if not hasattr(self.model, '_shards'):
            return
        if self.model not in created_models:
            return
        if self.model._shards.is_master:
            super(PartitionSequenceField, self).create_sequence(created_models, **kwargs)
        elif self.model._shards.num == 0:
            parent = self.model._shards.parent
            parent._meta.get_field_by_name(self.name)[0].create_sequence([parent])
