import json
import logging


class Writer:
    """Listens to a kafka topic and inserts them into our database"""
    KAFKA_POLL_TIMEOUT_MS = 1 * 1000

    def __init__(self, db_connector, kafka_connector, topic):
        self._db_connector = db_connector
        self._kafka_connector = kafka_connector
        self._topic = topic
        self._consumer = None
        self._db_connection = None

    def run(self):
        while True:
            try:
                # call inner run function, this will setup our connections again if something fails
                self._do_run()
            except Exception as e:
                logging.error("Caught exception while running", e)

    def _do_run(self):
        self._consumer = self._kafka_connector.create_consumer(self._topic)
        self._db_connection = self._db_connector.get_connection()

        try:
            while True:
                self._poll_once()
        finally:
            try:
                self._db_connection.close()
                self._db_connection = None
            except Exception:
                pass

            try:
                self._consumer.close()
                self._consumer = None
            except Exception:
                pass

    def _poll_once(self):
        part_and_messages = self._consumer.poll(timeout_ms=Writer.KAFKA_POLL_TIMEOUT_MS)
        with self._db_connection.cursor() as cur:
            try:
                for _, messages in part_and_messages.items():
                    for message in messages:
                        # if this proves to be a bottle-neck we can batch our inserts
                        self._decode_and_insert_message(message.value, cur)

                self._db_connection.commit()

                # mark messages as committed only after they're in the db
                self._consumer.commit()
            except Exception as e:
                logging.error("Caught error polling, rolling back", e)
                self._db_connection.rollback()
            finally:
                cur.close()

    def _decode_and_insert_message(self, message: bytes, cursor):
        decoded = json.loads(message)

        # insert result into database, conflicts can be ignored since we may have written the
        # entry in a previous aborted batch
        cursor.execute(
            "INSERT INTO check_results(check_id, check_result_id, check_started_at, "
            " http_response_code, regex_matched, response_time_ms) "
            "  VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
            (
                decoded['check_id'], decoded['check_result_id'], decoded['start_time'],
                decoded['status_code'], decoded['matched'], decoded['time_taken_ms']
            )
        )
