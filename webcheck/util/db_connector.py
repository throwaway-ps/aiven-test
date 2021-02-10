import logging
import psycopg2
from urllib.parse import urlparse


class DbConnector:
    """Database connector for PostgreSQL"""

    def __init__(self, db_config, test_connection=True):
        """Construct given a db_config. Raises if the connection fails

        :arg db_config: Connection string in the form pg://user:pass@host:port/database
        """
        self._parse_kwargs_from_uri(db_config)

        # check if we can connect, makes it easier to spot in a log-file if that is done early
        try:
            self.get_connection().close()
        except psycopg2.OperationalError as e:
            logging.error("Could not connect to the database", e)
            raise

    def _parse_kwargs_from_uri(self, db_config):
        """Parses the connection string, our OR-Mapper would probably have a
        helper for that..."""
        url = urlparse(db_config)
        self._connection_kwargs = {
            'user': url.username,
            'password': url.password,
            'host': url.hostname,
            'port': url.port,
            'dbname': url.path.strip('/')
        }
        logging.info(
            "Using database {} on {}:{} with user {}".format(
                self._connection_kwargs['dbname'],
                self._connection_kwargs['host'],
                self._connection_kwargs['port'],
                self._connection_kwargs['user']
            )
        )

    def get_connection(self):
        return psycopg2.connect(**self._connection_kwargs)
