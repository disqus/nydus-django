"""
djnydus.router
~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from nydus.db.routers import BaseRouter


class OrmRouter(BaseRouter):
    def get_dbs(self):
        return []
