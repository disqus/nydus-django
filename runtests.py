#!/usr/bin/env python
import sys
from os.path import dirname, abspath
from optparse import OptionParser

sys.path.insert(0, dirname(abspath(__file__)))

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'djnydus.db.backend',
                'OPTIONS': {
                    'hosts': {
                        0: {'backend': 'django.db.backends.sqlite3', 'name': ':memory:'},
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

from django_nose import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']

    kwargs.setdefault('interactive', False)

    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
