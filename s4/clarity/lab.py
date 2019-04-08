# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import FieldsMixin, ClarityElement


class Lab(FieldsMixin, ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/lab}lab"
    ATTACH_TO_NAME = "ClientLab"
