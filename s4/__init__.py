# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from pkgutil import extend_path

# Allows merging the s4 namespace during package install. Required for Python versions < 3.3
__path__ = extend_path(__path__, __name__)
