# Copyright 2025 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity._internal import ClarityElement
from s4.clarity._internal.props import subnode_links, subnode_property
from .process_type import ProcessType


class InstrumentType(ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/latest/data_itp.html#element_instrument-type
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/instrumenttype}instrument-type"

    name = subnode_property("name")
    vendor = subnode_property("vendor")
    process_types = subnode_links(ProcessType, "process-type", "process-types")

    def __eq__(self, other):
        """comparison operator overloading,
        If it's a string, check against the name, otherwise check against its URI.
        This allows for backwards compatibility with the old `Instrument.instrument_type` which is a string.
        An issue in v1.6.0 - in which the `Instrument.instrument_type` was a string.

        Args:
            other (str | ClarityElement | object): the other object to compare against

        Returns:
            bool: True if the instrument type is equal to the other object, False otherwise
        """
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, ClarityElement):
            return self.uri == other.uri
        return False

    def __ne__(self, other):
        """comparison operator overloading,
        If it's a string, check against the name, otherwise check against its URI.
        This allows for backwards compatibility with the old `Instrument.instrument_type` which is a string.
        An issue in v1.6.0 - in which the `Instrument.instrument_type` was a string.

        Args:
            other (str | ClarityElement | object): the other object to compare against

        Returns:
            bool: True if the instrument type is not equal to the other object, False otherwise
        """
        if isinstance(other, str):
            return self.name != other
        elif isinstance(other, ClarityElement):
            return self.uri != other.uri
        return True
