#!/usr/bin/env python
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'djnydus.db.backend',
                'OPTIONS': {
                    'defaults': {
                        'backend': 'django.db.backends.sqlite3',
                        'name': ':memory:'
                    },
                    'hosts': {
                        0: {},
                        1: {},
                    },
                }
            },
            # 'psycopg2': {
            #     'ENGINE': 'nydus.contrib.django.backend',
            #     'NAME': 'django/psycopg2',
            # },
        },
        INSTALLED_APPS=[
            'djnydus',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
    )
