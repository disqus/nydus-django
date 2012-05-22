#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

try:
    import multiprocessing
except:
    pass

if 'nosetests' in sys.argv:
    setup_requires = ['nose']
else:
    setup_requires = []

tests_require = [
    'coverage',
    'django-nose',
    'Django>=1.2,<1.5',
    'mock==0.8',
    'nose>=1.0',
    'pep8',
    'pyflakes',
    'psycopg2',
    'unittest2',
]

install_requires = [
    'nydus>=0.9.0',
    'Django>=1.2,<1.5',
]

dependency_links = [
    'https://github.com/dcramer/pyflakes/tarball/master#egg=pyflakes',
]

setup(
    name='nydus-django',
    version='0.1.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/disqus/nydus-django',
    description='Connection utilities for Nydus and Django',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
