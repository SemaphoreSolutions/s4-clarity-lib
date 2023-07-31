# Copyright 2021 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity.instrument import Instrument
from s4.clarity.step import Step, StepDetails

from utils.generic_testcases import LimsTestCase

from datetime import date  # typing
from s4.clarity.utils.date_util import str_to_date


class TestInstrument(LimsTestCase):

    def test_instrument_assignment_on_step_details(self):
        """
        Test for Instrument set in the 'Instrument Field' value during the Step Details phase
        """

        # Parse the xml into a StepDetails object
        step = self.element_from_xml(Step, STEP_XML)  # type: Step

        # pre instrument used field set
        step_details = self.element_from_xml(StepDetails, PRE_INSTRUMENT_SET_STEP_DETAILS_XML, step=step)  # type: StepDetails
        self.assertIsNone(step_details.instrument_used)

        # post instrument used field set
        step_details = self.element_from_xml(StepDetails, POST_INSTRUMENT_SET_STEP_DETAILS_XML, step=step)
        self.assertIsNotNone(step_details.instrument_used)

    def test_instrument_object_properties(self):
        """
        Test for Instrument object instantiation (Clarity Element inherits WrappedXml class)
        Point of Interest: Instrument API endpoint only permits GET
        """

        # Parse the xml into an Instrument object
        instrument = self.element_from_xml(Instrument, INSTRUMENT_XML)  # type: Instrument

        self.assertEqual(instrument.name, "instrument_2")
        self.assertEqual(instrument.limsid, "4")
        self.assertEqual(instrument.instrument_type, "Instrument ABC")
        self.assertEqual(instrument.serial_number, "2222")
        self.assertEqual(instrument.archived, False)

        clarity_date_time_str = "2021-12-06"
        expected_date = str_to_date(clarity_date_time_str)  # type: date

        self.assertEqual(instrument.expiry_date, expected_date)


STEP_XML = \
    """
    <stp:step xmlns:stp="http://genologics.com/ri/step" current-state="Record Details" limsid="24-6859" uri="https://qalocal/api/v2/steps/24-6859">
    <configuration uri="https://qalocal/api/v2/configuration/protocols/12/steps/29">Visual QC</configuration>
    <date-started>2021-11-24T11:06:46.014-08:00</date-started>
    <actions uri="https://qalocal/api/v2/steps/24-6859/actions"/>
    <details uri="https://qalocal/api/v2/steps/24-6859/details"/>
    <available-programs/>
    </stp:step>
    """

PRE_INSTRUMENT_SET_STEP_DETAILS_XML = \
    """
    <stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/24-6859/details">
    <step uri="https://qalocal/api/v2/steps/24-6859" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/12/steps/29">Visual QC</configuration>
    <input-output-maps>
    <input-output-map>
    <input uri="https://qalocal/api/v2/artifacts/1C-752PA1" limsid="1C-752PA1"/>
    <output uri="https://qalocal/api/v2/artifacts/92-55059" output-generation-type="PerAllInputs" type="ResultFile" limsid="92-55059"/>
    </input-output-map>
    </input-output-maps>
    <fields/>
    </stp:details>
    """

POST_INSTRUMENT_SET_STEP_DETAILS_XML = \
    """
    <stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/24-6859/details">
    <step uri="https://qalocal/api/v2/steps/24-6859" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/12/steps/29">Visual QC</configuration>
    <input-output-maps>
    <input-output-map>
    <input uri="https://qalocal/api/v2/artifacts/1C-752PA1" limsid="1C-752PA1"/>
    <output uri="https://qalocal/api/v2/artifacts/92-55059" output-generation-type="PerAllInputs" type="ResultFile" limsid="92-55059"/>
    </input-output-map>
    </input-output-maps>
    <fields/>
    <instrument uri="https://qalocal/api/v2/instruments/4">instrument_2</instrument>
    </stp:details>
    """

INSTRUMENTS_XML = \
    """
    <inst:instruments xmlns:inst="http://genologics.com/ri/instrument">
    <instrument uri="https://qalocal/api/v2/instruments/2">
    <name>non_an_instrument</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/3">
    <name>instrument_1</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/4">
    <name>instrument_2</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/5">
    <name>instrument_3</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/6">
    <name>instrument_a</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/7">
    <name>instrument_b</name>
    </instrument>
    <instrument uri="https://qalocal/api/v2/instruments/8">
    <name>instrument_c</name>
    </instrument>
    </inst:instruments>
    """

INSTRUMENT_XML = \
    """
    <inst:instrument xmlns:inst="http://genologics.com/ri/instrument" limsid="55-4" uri="https://qalocal/api/v2/instruments/4">
    <name>instrument_2</name>
    <type>Instrument ABC</type>
    <serial-number>2222</serial-number>
    <expiry-date>2021-12-06</expiry-date>
    <archived>false</archived>
    </inst:instrument>
    """
