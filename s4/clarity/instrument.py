# Copyright 2021 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property
from s4.clarity import types, lazy_property


class Instrument(ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/5.3/rest.version.instruments.html
    Note: See example xml_root below --
        <inst:instrument xmlns:inst="http://genologics.com/ri/instrument" limsid="55-6" uri="https://clarityhost/api/v2/instruments/6">
        We use uri id for Instrument object limsid i.e. "6" instead of "55-6"

    Cautionary Notes:
    In most cases, a Step UDF or Reagent Kit/Reagent Lot is a better option to track instrument use in the LIMS.
    Consider --
    1. Instrument API endpoint only permits GET
    2. You may configure multiple Instruments to step. However, you can only assign 1 Instrument per step
    3. If Instrument is configured to step, Step UDFs CAN NOT be set via the API,
        until the Instrument field is set via UX/UI
    4. Instruments are not part of the ETL that supports the Illumina Reporting Module
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
        :type: List[Instrument]
        """
        instruments = self.lims.instruments.all()
        return [instrument for instrument in instruments
                if instrument.instrument_type == self.instrument_type]
