from django.test import TestCase

from djnydus.db import DjangoDatabase


class DjangoConnectionsTest(TestCase):
    def test_simple(self):
        from django.db import connections

        cursor = connections['default'].cursor()
        cursor.execute('SELECT 1')
        self.assertEquals(cursor.fetchone(), (1,))


class DjangoDatabaseTest(TestCase):
    def setUp(self):
        from django.db.backends import sqlite3

        self.db = DjangoDatabase(sqlite3, name=':memory:', num=0)

    def test_proxy(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT 1')
        self.assertEquals(cursor.fetchone(), (1,))

    def test_provides_identififer(self):
        self.assertEqual(
            "django.db.backends.sqlite3 HOST=None NAME=:memory: OPTIONS={} PASSWORD=None PORT=None TEST_NAME=None USER=None",
            self.db.identifier
        )

# class DjangoPsycopg2Test(BaseTest):
#     def setUp(self):
#         from django.db.backends import postgresql_psycopg2
#
#         self.db = DjangoDatabase(postgresql_psycopg2, name='nydus_test', num=0)
#
#     def test_proxy(self):
#         cursor = self.db.execute('SELECT 1')
#         self.assertEquals(cursor.fetchone(), (1,))
#
#     def test_with_cluster(self):
#         p = Cluster(
#             hosts={0: self.db},
#         )
#         cursor = p.execute('SELECT 1')
#         self.assertEquals(cursor.fetchone(), (1,))
