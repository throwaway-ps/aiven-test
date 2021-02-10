import os
from typing import Any, Optional


class Config:
    def __init__(self):
        self._db_config = os.environ.get('POSTGRES_CONNECTION')
        self._kafka_bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
        self._kafka_cert_dir = os.environ.get('KAFKA_CERT_DIR')

    @staticmethod
    def _return_or_raise(val: Optional[str], val_desc: str) -> str:
        if val is None:
            raise ValueError('Missing environment value "{}"'.format(val_desc))

        return val

    db_config = property(
        lambda self: Config._return_or_raise(self._db_config, 'POSTGRES_CONNECTION'))
    kafka_bootstrap_servers = property(
        lambda self: Config._return_or_raise(self._kafka_bootstrap_servers, 'KAFKA_BOOTSTRAP_SERVERS'))
    kafka_cert_dir = property(
        lambda self: Config._return_or_raise(self._kafka_cert_dir, 'KAFKA_CERT_DIR'))
