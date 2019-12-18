# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from unittest import TestCase

import s4.clarity._internal.element
import s4.clarity._internal.factory


class TestFlags(TestCase):

    def test_flags(self):
        """
        Are flags sane?
        """
        self.assertTrue(
            s4.clarity._internal.element.BatchFlags.BATCH_ALL & s4.clarity._internal.element.BatchFlags.BATCH_CREATE
        )
        self.assertFalse(
            s4.clarity._internal.element.BatchFlags.BATCH_ALL & s4.clarity._internal.element.BatchFlags.NONE
        )
