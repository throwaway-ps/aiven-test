import json
import logging
import sched
from typing import List
import uuid

from webcheck.util import KafkaConnector
from .check_runner import CheckRunner


class Checker:
    """Runs check provided in constructor and sends it to a kafka topic"""

    def __init__(self, kafka_connector: KafkaConnector, topic: str, check_runner: CheckRunner, checks: List[dict]):
        self._kafka_connector = kafka_connector
        self._topic = topic
        self._check_runner = check_runner
        self._checks = checks
        self._scheduler = sched.scheduler()
        self._producer = None

    def run(self):
        try:
            self._producer = self._kafka_connector.create_producer()
        except Exception as e:
            logging.fatal('Could not create producer', e)
            raise e

        for check in self._checks:
            # schedule checks with no delay to get started
            self._schedule(check, immediately=True)

        logging.info('Checker running...')
        self._scheduler.run(blocking=True)

    def _schedule(self, check, immediately=False):
        """Schedules a check for on-time execution using its check-interval (or immediately)"""
        delay = 0 if immediately else check['check_interval_seconds']
        self._scheduler.enter(delay, 0, lambda: self._run_one(check))

    def _run_one(self, check):
        """Runs the check, collects the result and sends it to topic"""
        try:
            run_uuid = str(uuid.uuid4())
            logging.info(
                'Running check {} with uri {} and run-id {}'.format(check['check_id'], check['uri'], run_uuid)
            )

            try:
                check_result = self._check_runner.run_check(check, run_uuid)
                self._send_result(check_result)
            except Exception as e:
                # catch all exceptions to prevent the scheduler from aborting
                logging.error("Error checking {} on run {}".format(check['check_id'], run_uuid), e)

            logging.debug("{} Done.".format(run_uuid))
        finally:
            # reschedule the check
            self._schedule(check)

    def _send_result(self, check_result: dict):
        """Sends one check-result to the kafka topic"""
        self._producer.send(
            self._topic,
            json.dumps(check_result).encode('utf-8')
        )
