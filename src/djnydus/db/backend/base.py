"""
djnydus.db.backend
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys

from django.db import DEFAULT_DB_ALIAS
from django.db.backends.creation import TEST_DATABASE_PREFIX
from django.core.exceptions import ImproperlyConfigured
from nydus.db import create_cluster


class DatabaseIntrospection(object):
    def __init__(self, connection, cluster):
        self.connection = connection
        self.cluster = cluster

    def __getattr__(self, attr):
        return getattr(self.cluster.hosts[0].introspection, attr)


class DatabaseCreation(object):
    def __init__(self, connection, cluster):
        self.connection = connection
        self.cluster = cluster

    def create_test_db(self, *args, **kwargs):
        supports_trans = True
        for connection in self.cluster.hosts.itervalues():
            connection.creation.create_test_db(*args, **kwargs)
            if not connection.settings_dict.get('SUPPORTS_TRANSACTIONS'):
                supports_trans = False

        self.connection.settings_dict['SUPPORTS_TRANSACTIONS'] = supports_trans
        return self._get_test_db_name()

    def destroy_test_db(self, *args, **kwargs):
        for connection in self.cluster.hosts.itervalues():
            connection.creation.destroy_test_db(*args, **kwargs)

    def test_db_signature(self):
        """
        Returns a tuple with elements of self.connection.settings_dict (a
        DATABASES setting value) that uniquely identify a database
        accordingly to the RDBMS particularities.
        """
        settings_dict = self.connection.settings_dict
        return (
            settings_dict['HOST'],
            settings_dict['PORT'],
            settings_dict['ENGINE'],
            settings_dict['NAME']
        )

    def _get_test_db_name(self):
        if self.connection.settings_dict.get('TEST_NAME'):
            test_database_name = self.connection.settings_dict['TEST_NAME']
        else:
            test_database_name = TEST_DATABASE_PREFIX + self.connection.settings_dict['NAME']

        return test_database_name


class DatabaseWrapper(object):
    def __init__(self, settings_dict, alias=DEFAULT_DB_ALIAS):
        self.settings_dict = settings_dict
        self.alias = alias

        options = settings_dict['OPTIONS']
        options.setdefault('backend', 'djnydus.db.DjangoDatabase')
        options.setdefault('router', 'djnydus.db.router.OrmRouter')

        try:
            self.cluster = create_cluster(options)
        except KeyError:
            exc_info = sys.exc_info()
            raise ImproperlyConfigured('%s: %s' % (exc_info[0].__name__, exc_info[1])), None, exc_info[2]

        self.creation = DatabaseCreation(self, self.cluster)
        self.introspection = DatabaseIntrospection(self, self.cluster)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self.cluster, name)
