#!/usr/bin/env python

from setuptools import setup, find_packages


tests_require = [
    'coverage',
    'flake8',
    'mock==0.8',
    'nose>=1.0',
    'pytest',
    'pytest-django-lite',
    'psycopg2',
]

install_requires = [
    'nydus>=0.9.0',
    'Django>=1.2,<1.5',
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
    extras_require={
        'tests': install_requires + tests_require,
    },
    install_requires=install_requires,
    tests_require=tests_require,
    include_package_data=True,
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
