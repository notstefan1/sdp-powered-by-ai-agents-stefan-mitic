"""Worker process - async event consumers (feed fan-out, notifications)."""

import logging
import os
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    log.info("Worker starting. DATABASE_URL=%s", bool(os.environ.get("DATABASE_URL")))
    # TODO: wire Redis Streams consumers for feed fan-out and notifications
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
