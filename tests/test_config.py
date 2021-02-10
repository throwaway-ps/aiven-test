import os
import unittest

from unittest import mock
from webcheck.util import Config


class TestConfig(unittest.TestCase):

    @mock.patch.dict(os.environ, {})
    def test_asserts_when_not_configured(self):
        self.assertRaises(ValueError, lambda: Config().db_config)
        self.assertRaises(ValueError, lambda: Config().kafka_bootstrap_servers)
        self.assertRaises(ValueError, lambda: Config().kafka_cert_dir)

    @mock.patch.dict(os.environ, {
        'POSTGRES_CONNECTION': 'a connection string',
        'KAFKA_BOOTSTRAP_SERVERS': 'bootstrap servers',
        'KAFKA_CERT_DIR': 'certificates be here'
    })
    def test_asserts_when_not_configured(self):
        self.assertEqual('a connection string', Config().db_config)
        self.assertEqual('bootstrap servers', Config().kafka_bootstrap_servers)
        self.assertEqual('certificates be here', Config().kafka_cert_dir)
