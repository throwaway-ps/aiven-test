from webcheck.util.config import Config
from webcheck.util.db_connector import DbConnector


def main():
    conf = Config()
    connector = DbConnector(conf.db_config)
    con = connector.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("""
CREATE TABLE check_results (
  check_result_id UUID PRIMARY KEY NOT NULL,
  check_id UUID NOT NULL,
  http_response_code INT,
  regex_matched BOOLEAN,
  check_started_at TIMESTAMP WITH TIME ZONE NOT NULL,
  response_time_ms INT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
            """)
            con.commit()
    finally:
        con.close()


if __name__ == '__main__':
    main()
