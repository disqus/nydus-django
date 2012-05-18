#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

if 'nosetests' in sys.argv:
    setup_requires = ['nose']
else:
    setup_requires = []

tests_require = [
    'Django>=1.2,<1.4',
    'mock',
    'nose',
    'psycopg2',
    'unittest2',
]


install_requires = [
    'nydus>=0.9.0',
]

setup(
    name='nydus-django',
    version='0.1.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/disqus/nydus-django',
    description='Connection utilities for Nydus and Django',
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    include_package_data=True,
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
