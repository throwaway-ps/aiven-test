import unittest

from unittest import mock
from webcheck.util import DbConnector


class TestDbConnector(unittest.TestCase):
    @mock.patch('psycopg2.connect')
    def test_it_connects_on_create(self, connect):
        """Should connect on construction"""
        DbConnector('pg://foo:bar@localhost:1234/thedb')
        connect.assert_called_with(
            **{
                'user': 'foo',
                'password': 'bar',
                'host': 'localhost',
                'port': 1234,
                'dbname': 'thedb'
            }
        )
