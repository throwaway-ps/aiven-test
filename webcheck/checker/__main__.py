import logging
import re

from webcheck.checker.check_runner import CheckRunner
from webcheck.util import Config
from webcheck.checker import Checker
from webcheck.util import KafkaConnector

checks = [
    {
        'check_id': 'f786d986-eafe-4a19-ab9f-8437331cec76',
        'uri': 'https://httpbin.org/status/404',
        'matcher': None,
        'check_interval_seconds': 15
    },
    {
        'check_id': '690b1064-bffd-4f98-be73-c1607407ba6a',
        'uri': 'https://httpbin.org/robots.txt',
        'matcher': re.compile('^Disallow:.*', re.DOTALL | re.MULTILINE),
        'check_interval_seconds': 3 * 60
    }
]


def main():
    conf = Config()
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting writer")
    kafka_connector = KafkaConnector(
        kafka_bootstrap_servers=conf.kafka_bootstrap_servers,
        kafka_cert_dir=conf.kafka_cert_dir,
    )
    runner = CheckRunner()
    c = Checker(
        kafka_connector=kafka_connector,
        topic='checks-v1',
        check_runner=runner,
        checks=checks
    )
    c.run()


if __name__ == '__main__':
    main()
