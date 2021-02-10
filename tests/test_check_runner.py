import re
import unittest
import uuid

from unittest import mock

from webcheck.checker.check_runner import CheckRunner


class TestChecker(unittest.TestCase):
    CHECK_WITHOUT_MATCHER = {
        'check_id': 'f786d986-eafe-4a19-ab9f-8437331cec76',
        'uri': 'https://httpbin.org/status/404',
        'matcher': None,
        'check_interval_seconds': 15
    }
    CHECK_WITH_MATCHER = {
        'check_id': '690b1064-bffd-4f98-be73-c1607407ba6a',
        'uri': 'https://httpbin.org/robots.txt',
        'matcher': re.compile('^Disallow:.*', re.DOTALL | re.MULTILINE),
        'check_interval_seconds': 3 * 60
    }

    def test_it_constructs(self):
        """Should construct without throwing"""
        CheckRunner()

    @mock.patch('webcheck.checker.checker.requests.get')
    def test_execute_check(self, request_get_mock):
        """Check that _execute_check works"""

        request_get_mock.return_value.status_code = 418

        result, run_uuid = self._run_check_with_mock(request_get_mock, self.CHECK_WITHOUT_MATCHER)

        self.assertEqual(self.CHECK_WITHOUT_MATCHER['check_id'], result['check_id'])
        self.assertEqual(run_uuid, result['check_result_id'])
        self.assertIsNotNone(result['time_taken_ms'])
        self.assertEqual(418, result['status_code'])
        self.assertIsNone(result['matched'], 'matched should be None if we do not have a matcher')
        self.assertIsNotNone(result['start_time'])

    @mock.patch('webcheck.checker.check_runner.requests.get')
    def test_execute_check_with_matcher_matching(self, request_get_mock):
        """We should return True if the matcher matches"""

        request_get_mock.return_value.status_code = 418
        request_get_mock.return_value.text = 'Disallow: you!'

        result, run_uuid = self._run_check_with_mock(request_get_mock, self.CHECK_WITH_MATCHER)

        self.assertEqual(self.CHECK_WITH_MATCHER['check_id'], result['check_id'])
        self.assertEqual(run_uuid, result['check_result_id'])
        self.assertIsNotNone(result['time_taken_ms'])
        self.assertEqual(418, result['status_code'])
        self.assertEqual(True, result['matched'])
        self.assertIsNotNone(result['start_time'])

    @mock.patch('webcheck.checker.check_runner.requests.get')
    def test_execute_check_with_matcher_not_matching(self, request_get_mock):
        """We should return False if the matcher matches

        This is basically a copy of the previous test, something with yielding test-cases interfered with
        the mocking annotators"""

        request_get_mock.return_value.status_code = 418
        request_get_mock.return_value.text = 'no match :('

        result, run_uuid = self._run_check_with_mock(request_get_mock, self.CHECK_WITH_MATCHER)

        self.assertEqual(False, result['matched'])

    def _run_check_with_mock(self, request_get_mock, check):
        runner = CheckRunner()
        run_uuid = uuid.uuid4()
        result = runner.run_check(
            check=check,
            run_uuid=run_uuid
        )
        request_get_mock.assert_called_once_with(
            check['uri'],
            timeout=CheckRunner.REQUEST_TIMEOUT_SECONDS,
            headers={
                'User-Agent': CheckRunner.USER_AGENT
            }
        )
        return result, run_uuid

    def test_scheduling(self):
        pass

    def test_checks_keep_scheduled(self):
        pass

    def test_tasks_are_scheduled_initially(self):
        pass
