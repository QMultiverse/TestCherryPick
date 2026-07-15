"""Shared variables consumed by Robot suites via ``Variables`` import."""

import os

# Environment selected at runtime, e.g. ``robot --variable ENV:qa``.
ENV = os.environ.get("TCP_ENV", "qa")

# Default tags applied to smoke runs.
SMOKE_TAGS = ["smoke"]

# Common HTTP status codes used in assertions.
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
