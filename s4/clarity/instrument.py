# Copyright 2021 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property
from s4.clarity import ETree, types, lazy_property


class Instrument(ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/latest/data_inst.html#instrument

    NOTE: In most cases, a Step UDF or Reagent Kit/Reagent Lot is a better
    option to track instrument use in the LIMS. If you choose to use
    Instruments, be aware that there are a number of caveats:

    1. You may configure multiple Instruments to step. However, you can only
    assign 1 Instrument per step.

    2. If Instrument is configured to step, Step UDFs CAN NOT be set via the API,
        until the Instrument field is set via UX/UI

    3. Instruments are not supported by the Illumina Reporting Module
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/instrument}instrument"

    name = subnode_property("name")
    serial_number = subnode_property("serial-number")
    expiry_date = subnode_property("expiry-date", types.DATE)
    archived = subnode_property("archived", types.BOOLEAN)

    @lazy_property
    def limsid(self):
        """:type: str"""
        if self._limsid is None:
            if self.xml_root is not None:
                self._limsid = self._xml_root.get('limsid')
            else:
                raise Exception("No limsid available because there is no xml_root set")
        return self._limsid

    @property
    def instrument_type(self):
        """:type: InstrumentType"""
        return self.lims.instrument_types.get_by_name(self.xml_find("./type").text)

    @instrument_type.setter
    def instrument_type(self, value):
        itype = self.xml_find("./type")
        if itype is None:
            itype = ETree.SubElement(self.xml_root, "type")
        itype.text = value.name

    @lazy_property
    def related_instruments(self):
        """
        :return: List of instruments of the same instrument type
        :type: List[InstrumentType]
        """
        instruments = self.lims.instruments.all()
        return [instrument for instrument in instruments
                if instrument.instrument_type == self.instrument_type]
