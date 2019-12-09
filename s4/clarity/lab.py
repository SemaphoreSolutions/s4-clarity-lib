# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity._internal.factory import BatchFlags
from ._internal import FieldsMixin, ClarityElement


class Lab(FieldsMixin, ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/lab}lab"
    BATCH_FLAGS = BatchFlags.QUERY
    ATTACH_TO_NAME = "ClientLab"
