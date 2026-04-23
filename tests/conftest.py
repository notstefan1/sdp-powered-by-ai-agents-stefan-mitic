"""pytest configuration - enable in-memory mode for unit tests."""

import os

# Unit tests run without real infrastructure.
# Integration tests (test_db.py, test_integration.py) are skipped unless
# DATABASE_URL is set in the environment (i.e. inside Docker with postgres running).
if not os.environ.get("DATABASE_URL"):
    os.environ["TESTING"] = "1"
