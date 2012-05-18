"""
djnydus.shards.utils
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from functools import wraps


def resend_signal(new_sender):
    @wraps(new_sender)
    def wrapped(**kwargs):
        signal = kwargs.pop('signal')
        kwargs['sender'] = new_sender
        signal.send(**kwargs)
    return wrapped


def get_cluster_sizes(connections):
    """
    Returns a dictionary mapping clusters of servers (given
    by their naming scheme) and the number of connections in
    that cluster.
    """
    import re
    expr = re.compile(r'.*\.shard\d+$')
    clusters = {}
    for conn in connections:
        if not expr.match(conn):
            continue
        cluster = conn.split('.shard', 1)[0]
        if cluster not in clusters:
            clusters[cluster] = 1
        else:
            clusters[cluster] += 1
    return clusters
