import datetime
import logging
import requests
import time
from typing import Optional


class CheckRunner:
    """Runs single checks"""
    REQUEST_TIMEOUT_SECONDS = 10
    USER_AGENT = 'online-checker-demo 0.1'

    def run_check(self, check, run_uuid):
        """Runs the check and returns the result as a message"""
        response = None
        end_time = None
        start_time = time.time()
        try:
            # send request with timeout to not (potentially) hold back all other checks
            # TODO: limit response size to avoid memory starvation
            response = requests.get(
                check['uri'],
                timeout=self.REQUEST_TIMEOUT_SECONDS,
                headers={
                    'User-Agent': self.USER_AGENT  # allow us to be blocked
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
