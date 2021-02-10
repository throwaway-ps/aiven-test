import unittest

from unittest import mock

from webcheck.writer import Writer


class TestWriter(unittest.TestCase):
    @mock.patch('webcheck.util.DbConnector')
    @mock.patch('webcheck.util.KafkaConnector')
    def test_it_constructs(self, kafka_connector_mock, db_connector_mock):
        """Should construct without throwing"""
        Writer(
            kafka_connector=kafka_connector_mock.return_value,
            db_connector=db_connector_mock.return_value,
            topic='my-topic'
        )

    def test_records_get_written(self):
        pass

    def test_changes_get_rollbacked(self):
        # setup db
        # add side-effect to cursor.execute
        # assert that connection.rollback() is executed
        # assert that connection.commit() is not executed
        # assert that consumer.commit() ist not executed
        pass

    def test_kafka_is_not_commited(self):
        # setup db
        # add side-effect to connection.commit()
        # assert that consumer.commit() ist not executed
        pass
