nydus-django
============

.. note:: This package was formerly ``nydus.contrib.django``, but is not backwards compatible.

Partitioned Models
------------------

Add a Nydus connection to your settings:

::

        DATABASES = {
            'myshards': {
                'ENGINE': 'djnydus.db',
                'NAME': 'django/myshards',
            },
        }

        NYDUS_CONFIG = {
            'CONNECTIONS': {
                'django/myshards': {
                    'engine': 'djnydus.db.DjangoDatabase',
                    'defaults': {
                        'backend': 'django.db.backends.postgresql_psycopg2', 
                        'name': 'myshards',
                    }
                    'hosts': {
                        0: {'host': '192.168.0.100'},
                        1: {'host': '192.168.0.101'},
                        2: {'host': '192.168.0.102'},
                        3: {'host': '192.168.0.103'},
                    },
                },
            },
        }


Extend the PartitionModel class when creating your models:

::

    from django.db import models
    from djnydus.db.shards import PartitionModel, PartitionSequenceField

    class MyModel(PartitionModel):
        user_id = models.PositiveIntegerField()

        class Shards:
            key = 'user_id'
            cluster = 'myshards'
            size = 1024

Query the nodes passing in your ``key``:

::

    objects = MyModel.objects.filter(user_id=1)