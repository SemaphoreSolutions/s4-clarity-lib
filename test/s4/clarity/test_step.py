# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from datetime import datetime
from dateutil.tz import tzoffset, tzutc

from s4.clarity.artifact import Artifact
from s4.clarity.container import Container
from utils.generic_testcases import LimsTestCase
from s4.clarity.step import Step, StepActions, StepPlacements


class TestIomaps(LimsTestCase):

    def test_all_properties(self):

        # Parse the xml into a StepDetails object
        step = self.element_from_xml(Step, STEP_XML)

        self.assertEqual(step.name, "Step Config Name")

        expected_start_date = datetime(2017, 8, 21, 11, 52, 41, 350000, tzinfo=tzoffset(None, -25200))
        expected_end_date = datetime(2017, 8, 21, 11, 52, 46, 236000, tzinfo=tzoffset(None, -25200))

        self.assertEqual(step.date_started, expected_start_date)
        self.assertEqual(step.date_completed, expected_end_date)

    def test_missing_date_completed(self):
        step = self.element_from_xml(Step, NO_DATE_COMPLETED_XML)
        self.assertEqual(step.date_completed, None)

    def test_step_actions(self):
        step_actions = self.element_from_xml(StepActions, MANAGER_REVIEW_STEP_ACTIONS)

        # Make sure we are correctly reading the sub nodes.
        self.assertEqual(step_actions.escalation_author.uri, "https://qalocal/api/v2/researchers/3")
        self.assertEqual(step_actions.escalation_reviewer.uri, "https://qalocal/api/v2/researchers/3")
        self.assertEqual(step_actions.escalation_date, datetime(2017, 10, 18, 21, 39, 44, 567000, tzinfo=tzutc()))
        self.assertEqual(step_actions.escalated_artifacts[0].uri, "https://qalocal/api/v2/artifacts/2-13081")

    def test_placement(self):
        step_placements = self.element_from_xml(StepPlacements, PLACEMENT_XML)
        container = self.element_from_xml(Container, CONTAINER_XML)
        p = step_placements.placements
        self.assertEqual(len(p),3)
        step_placements.clear_placements()
        p = step_placements.placements
        self.assertEqual(len(p),0)
        container = self.element_from_xml(Container, CONTAINER_XML)
        artifact = self.element_from_xml(Artifact, ARTIFACT_XML)
        step_placements.create_placement_with_no_location(artifact)
        step_placements.create_placement(artifact,container,"A5")
        p = step_placements.placements
        self.assertEqual(len(p),2)
        self.assertEqual(p[0].location_value, None)
        self.assertEqual(p[1].location_value, "A5")


STEP_XML = """
<stp:step xmlns:stp="http://genologics.com/ri/step" current-state="Assign Next Steps" limsid="24-4016" uri="https://qalocal/api/v2/steps/24-4016">
    <configuration uri="https://qalocal/api/v2/configuration/protocols/1/steps/1">Step Config Name</configuration>
    <date-started>2017-08-21T11:52:41.350-07:00</date-started>
    <date-completed>2017-08-21T11:52:46.236-07:00</date-completed>
    <actions uri="https://qalocal/api/v2/steps/24-4016/actions"/>
    <program-status uri="https://qalocal/api/v2/steps/24-4016/programstatus"/>
    <details uri="https://qalocal/api/v2/steps/24-4016/details"/>
    <available-programs>
        <available-program name="EPP Script 1" uri="https://qalocal/api/v2/steps/24-3818/trigger/50"/>
        <available-program name="EPP Script 2" uri="https://qalocal/api/v2/steps/24-3818/trigger/54"/>
    </available-programs>
</stp:step>"""


NO_DATE_COMPLETED_XML = """
<stp:step xmlns:stp="http://genologics.com/ri/step" current-state="Assign Next Steps" limsid="24-4016" uri="https://qalocal/api/v2/steps/24-4016">
    <configuration uri="https://qalocal/api/v2/configuration/protocols/1/steps/1">Step Config Name</configuration>
    <date-started>2017-08-21T11:52:41.350-07:00</date-started>
    <actions uri="https://qalocal/api/v2/steps/24-4016/actions"/>
    <program-status uri="https://qalocal/api/v2/steps/24-4016/programstatus"/>
    <details uri="https://qalocal/api/v2/steps/24-4016/details"/>
<available-programs/>
</stp:step>"""


MANAGER_REVIEW_STEP_ACTIONS = """
<stp:actions xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/24-3098/actions">
    <step uri="https://qalocal/api/v2/steps/24-3098" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/5/steps/18">Review Step</configuration>
    <next-actions>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="completerepeat" artifact-uri="https://qalocal/api/v2/artifacts/2-13081"/>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="nextstep" artifact-uri="https://qalocal/api/v2/artifacts/2-13080"/>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="nextstep" artifact-uri="https://qalocal/api/v2/artifacts/2-13082"/>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="nextstep" artifact-uri="https://qalocal/api/v2/artifacts/2-13083"/>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="nextstep" artifact-uri="https://qalocal/api/v2/artifacts/2-13084"/>
        <next-action step-uri="https://qalocal/api/v2/configuration/protocols/5/steps/19" action="nextstep" artifact-uri="https://qalocal/api/v2/artifacts/2-13085"/>
    </next-actions>
    <escalation>
        <request>
            <author uri="https://qalocal/api/v2/researchers/3">
                <first-name>API</first-name>
                <last-name>Access</last-name>
            </author>
            <reviewer uri="https://qalocal/api/v2/researchers/3">
                <first-name>API</first-name>
                <last-name>Access</last-name>
            </reviewer>
            <date>2017-10-18T21:39:44.567+00:00</date>
        </request>
        <escalated-artifacts>
            <escalated-artifact uri="https://qalocal/api/v2/artifacts/2-13081"/>
        </escalated-artifacts>
    </escalation>
</stp:actions>"""

PLACEMENT_XML = """
<stp:placements xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/24-147/placements">
    <step uri="https://qalocal/api/v2/steps/24-147" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/1/steps/1">Step Config Name</configuration>
    <selected-containers>
        <container uri="https://qalocal/api/v2/containers/27-93"/>
    </selected-containers>
    <output-placements>
        <output-placement uri="https://qalocal/api/v2/artifacts/2-283">
        </output-placement>
        <output-placement uri="https://qalocal/api/v2/artifacts/2-284">
        </output-placement>
        <output-placement uri="https://qalocal/api/v2/artifacts/2-285">
        </output-placement>
    </output-placements>
</stp:placements>
"""

CONTAINER_XML = """
<con:container xmlns:udf="http://genologics.com/ri/userdefined" xmlns:con="http://genologics.com/ri/container" uri="https://qalocal/api/v2/containers/27-1438" limsid="27-1438">
    <name>27-1438</name>
    <occupied-wells>0</occupied-wells>
    <state>Populated</state>
</con:container>"""

ARTIFACT_XML = """
<art:artifact xmlns:udf="http://genologics.com/ri/userdefined" xmlns:file="http://genologics.com/ri/file" xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/ADM51A11PA1?state=178" limsid="ADM51A11PA1">
    <name>Test Artifact</name>
    <type>Analyte</type>
    <output-type>Analyte</output-type>
    <qc-flag>UNKNOWN</qc-flag>
    <location>
        <container uri="https://qalocal/api/v2/containers/27-1438" limsid="27-94"/>
        <value>1:1</value>
    </location>
    <working-flag>true</working-flag>
    <sample uri="https://qalocal/api/v2/samples/ADM51A11" limsid="ADM51A11"/>
</art:artifact>
"""