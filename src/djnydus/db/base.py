"""
djnydus.db.base
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

from nydus import conf
from nydus.db.backends import BaseConnection
from nydus.utils import import_string

from django.conf import settings

__all__ = ('DjangoDatabase',)


def configure(settings):
    connections = getattr(settings, 'NYDUS_CONNECTIONS', {})

    conf.configure({'CONNECTIONS': connections})

configure(settings)


class DjangoDatabase(BaseConnection):
    def __init__(self, backend, name, host=None, port=None, test_name=None,
                       user=None, password=None, options={}, **kwargs):
        """
        Given an alias (which is defined in DATABASES), creates a new connection
        that proxies the original database engine.
        """
        if isinstance(backend, basestring):
            backend = import_string(backend)
        self.backend = backend
        self.settings_dict = {
            'ENGINE': backend,
            'HOST': host,
            'PORT': port,
            'NAME': name,
            'TEST_NAME': test_name,
            'OPTIONS': options,
            'USER': user,
            'PASSWORD': password,
        }
        self.wrapper = __import__('%s.base' % (backend.__name__,), {}, {}, ['DatabaseWrapper']).DatabaseWrapper(self.settings_dict)
        super(DjangoDatabase, self).__init__(**kwargs)

    def connect(self):
        # force django to connect
        self.wrapper.cursor()
        return self.wrapper

    def disconnect(self):
        self.wrapper.close()

    @property
    def identifier(self):
        settings = ["%s=%s" % i for i in sorted(self.settings_dict.items()) if i[0] != 'ENGINE']
        return '%s %s' % (self.backend.__name__, ' '.join(settings))
