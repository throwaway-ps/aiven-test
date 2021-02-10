from kafka import KafkaConsumer, KafkaProducer
import os


class KafkaConnector:
    """Creates a connection to Kafka, validates connection arguments"""
    KAFKA_CA_FILE = 'ca.pem'
    KAFKA_CERT_FILE = 'service.cert'
    KAFKA_KEY_FILE = 'service.key'

    def __init__(self, kafka_bootstrap_servers, kafka_cert_dir):
        self._kafka_bootstrap_servers = kafka_bootstrap_servers
        self._kafka_cert_dir = kafka_cert_dir
        self._validate_cert_dir()

    def _validate_cert_dir(self):
        """Sanity check that all files are present, obviously there are time-of-check vs. time-of-use issues here but
        the kafka client will fail if the files are not here"""
        if any([
            not os.path.exists(self._cert_file(KafkaConnector.KAFKA_CA_FILE)),
            not os.path.exists(self._cert_file(KafkaConnector.KAFKA_CERT_FILE)),
            not os.path.exists(self._cert_file(KafkaConnector.KAFKA_KEY_FILE)),
        ]):
            raise ValueError('Missing certificate file')

    def _cert_file(self, file_name: str):
        return os.path.join(self._kafka_cert_dir, file_name)

    def create_producer(self) -> KafkaProducer:
        """Creates a new producer"""
        # See: https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
        return KafkaProducer(
            **self._common_connection_args()
        )

    def create_consumer(self, topic: str) -> KafkaConsumer:
        """Creates a new consumer for the given topic"""
        # See: https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
        return KafkaConsumer(
            topic,
            **self._common_connection_args(),
            auto_offset_reset="earliest",
            client_id="demo-client-1",
            group_id="demo-group",
        )

    def _common_connection_args(self) -> dict:
        return {
            'bootstrap_servers': self._kafka_bootstrap_servers,
            'security_protocol': 'SSL',
            'ssl_cafile': self._cert_file(KafkaConnector.KAFKA_CA_FILE),
            'ssl_certfile': self._cert_file(KafkaConnector.KAFKA_CERT_FILE),
            'ssl_keyfile': self._cert_file(KafkaConnector.KAFKA_KEY_FILE),
        }
