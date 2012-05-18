"""
djnydus
~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('nydus-django').version
except Exception, e:
    VERSION = 'unknown'
