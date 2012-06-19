"""
djnydus.db.router
~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import random

from nydus.db.routers import BaseRouter


class OrmRouter(BaseRouter):
    def get_dbs(self, *args, **kwargs):
        db_list = super(OrmRouter, self).get_dbs(*args, **kwargs)

        return [random.choice(db_list)]
