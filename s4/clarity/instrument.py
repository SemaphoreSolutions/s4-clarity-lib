# Copyright 2021 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property
from s4.clarity import types, lazy_property


class Instrument(ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/5.3/rest.version.instruments.html
    Note: limsid attribute in xml root e.g. "55-x" does not have use in API, using uri id for Instrument object limsid
        <inst:instrument xmlns:inst="http://genologics.com/ri/instrument" limsid="55-x" uri="https://clarityhost/api/v2/instruments/6">
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/instrument}instrument"

    name = subnode_property("name")
    instrument_type = subnode_property("type")
    serial_number = subnode_property("serial-number")
    expiry_date = subnode_property("expiry-date", types.DATE)
    archived = subnode_property("archived", types.BOOLEAN)

    @lazy_property
    def related_instruments(self):
        """
        :return: List of instruments of the same instrument type
        :rtype: List[Instrument]
        Note: Clarity 5.2+ does NOT permit duplicate instrument type entries via UX/UI
        """
        instruments = self.lims.instruments.all()
        return [instrument for instrument in instruments
                if instrument.instrument_type == self.instrument_type]
