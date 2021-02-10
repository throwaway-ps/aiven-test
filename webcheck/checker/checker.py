import datetime
import json
import logging
import requests
import sched
import time
from typing import List, Optional
import uuid

from webcheck.util.kafka_connector import KafkaConnector


class Checker:
    """Runs check provided in constructor and sends it to a kafka topic

    At the moment this class clearly does too many things. The next time we're changing something to the checks
    structure (or even decide where we get them from), we should pass them in as objects that can perform
    the checks themselves.
    """
    REQUEST_TIMEOUT_SECONDS = 10
    USER_AGENT = 'online-checker-demo 0.1'

    def __init__(self, kafka_connector: KafkaConnector, topic: str, checks: List[dict]):
        self._kafka_connector = kafka_connector
        self._topic = topic
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
                check_result = self._execute_check(check, run_uuid)
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

    def _execute_check(self, check, run_uuid):
        """Runs the check and returns the result as a message"""
        response = None
        end_time = None
        start_time = time.time()
        try:
            # send request with timeout to not (potentially) hold back all other checks
            # TODO: limit response size to avoid memory starvation
            response = requests.get(
                check['uri'],
                timeout=Checker.REQUEST_TIMEOUT_SECONDS,
                headers={
                    'User-Agent': Checker.USER_AGENT  # allow us to be blocked
                }
            )
            end_time = time.time()
        except Exception as e:
            logging.error('Caught exception while checking {}'.format(check['check_id']), e)

        # Set end_time even if we ran into an exception to get some kind of measurement back
        # we will not send a result-code that should indicate that something went wrong.
        # Also, this safes us from not having any time-reference if we don't get a response
        # (we could look at response.elapsed to get a time independent of the response-size)
        if end_time is None:
            end_time = time.time()

        return {
            'check_id': check['check_id'],
            'check_result_id': run_uuid,
            'time_taken_ms': (end_time - start_time) * 1000,
            'status_code': response.status_code,
            'matched': self._check_response_matches(response, check),
            'start_time': datetime.datetime.utcfromtimestamp(start_time).isoformat()
        }

    def _check_response_matches(self, response: requests.Response, check: dict) -> Optional[bool]:
        """Checks if the matcher matches anything in the response-text"""
        if 'matcher' in check and check['matcher'] is not None:
            matches = check['matcher'].findall(response.text)
            return matches is not None and len(matches) > 0
        else:
            return None
