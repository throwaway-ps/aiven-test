import logging
from webcheck.util import Config
from webcheck.util import DbConnector
from webcheck.util import KafkaConnector
from webcheck.writer import Writer


def main():
    conf = Config()
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting writer")
    db_connector = DbConnector(conf.db_config)
    kafka_connector = KafkaConnector(
        kafka_bootstrap_servers=conf.kafka_bootstrap_servers,
        kafka_cert_dir=conf.kafka_cert_dir
    )
    w = Writer(
        db_connector=db_connector,
        kafka_connector=kafka_connector,
        topic='checks-v1'
    )
    w.run()


if __name__ == '__main__':
    main()
