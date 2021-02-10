# Overview

This project consists of two parts:

1. A checker that periodically checks websites.
   
   The checks include a *URI* and an optional *regular-expression*. The regular-expression is run against 
   the returned body. The checker notes the response time, the http return code, as well as if the 
   regular-expression matched. Additionally each perfomed check is given a unique UUID for correlation
   and deduplication on the consumer side.
1. A writer that inserts the results into a postgresql database. The UUID of the check-run is used to prevent
  duplicated results.

The checker and the consumer are connected via a shared Kafka topic.

# Running

1. `POSTGRES_CONNECTION='pq://user:password@host:port/database' KAFKA_TOPIC='check_results' python -m webcheck.writer`
1. `KAFKA_BOOTSTRAP_SERVERS='localhost:1234' KAFKA_CERT_DIR=kafka-certs python -m webcheck.checker`

`KAFKA_CERT_DIR` is expected to hold `ca.pem`, `service.cert` and `service.key`

# Setup for Development

1. Create a virtualenv (see: https://docs.python-guide.org/dev/virtualenvs/#virtualenvwrapper)
1. Install postgresql dev libraries (libpq-dev on Ubuntu)
1. pip install -r requirements.txt
1. Create a database
1. Create database tables using `POSTGRES_CONNECTION='...' python -m webcheck.create_tables`

# Testing

Run tests using `python -m unittest discover`, also please add some, we're severly lacking in that department. For
testablity try to pass mockable objects instead of doing too many things in one class.

# Extending

At the moment all URIs to check are contained in the checker. That is obviously not scalable. Depending on
the architecture of the deployment the following options are open:
* A third coordinating service could be written to distribute the workload
configured in a database via Kafka
* Distribute the workload via configuration-management if there are just a few changes
* etc...

# Database design

* `check_results`
  * `check_id: UUID NOT NULL` - UUID of the check performed, not linked to any other table but will probably have an entry somewhere...
  * `check_result_id: UUID NOT NULL` - UUID assigned by the checker
  * `http_response_code: INT` - Response-Code
  * `regex_matched: BOOLEAN`
  * `check_started_at: TIMESTAMP WITH TIME ZONE NOT NULL` - Time when the check started
  * `response_time_ms: INT` - Response time in milliseconds
  * `created_at: TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP()` - Time of insertion
