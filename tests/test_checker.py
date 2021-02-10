import unittest

from unittest import mock

from webcheck.checker import Checker
from webcheck.checker.check_runner import CheckRunner


class TestChecker(unittest.TestCase):

    @mock.patch('webcheck.util.KafkaConnector')
    def test_it_constructs(self, connector_mock):
        """Should construct without throwing"""

        connector_inst = connector_mock.return_value

        Checker(
            kafka_connector=connector_inst,
            topic='my-topic',
            check_runner=CheckRunner(),
            checks=[]
        )

    def test_scheduling(self):
        pass

    def test_checks_keep_being_scheduled(self):
        pass

    def test_tasks_are_scheduled_initially(self):
        pass
