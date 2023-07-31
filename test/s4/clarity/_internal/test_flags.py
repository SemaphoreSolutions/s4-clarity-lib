# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from unittest import TestCase

from s4.clarity._internal.factory import BatchFlags


class TestFlags(TestCase):

    def test_flags(self):
        """
        Are flags sane?
        """
        self.assertTrue(
            BatchFlags.BATCH_ALL & BatchFlags.BATCH_CREATE
        )
        self.assertFalse(
            BatchFlags.BATCH_ALL & BatchFlags.NONE
        )
