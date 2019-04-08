# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity.step import StepDetails
from s4.clarity.test.generic_testcases import LimsTestCase


class TestIomaps(LimsTestCase):

    @staticmethod
    def artifact_dict_to_limsids_dict(artifact_dict):
        """
        :type artifact_dict: dict[Artifact, set[Artifact]]
        """
        limsids_dict = {}
        for key, value in artifact_dict.items():
            limsids_dict[key.limsid] = set([o.limsid for o in value])
        return limsids_dict

    def test_unpooling(self):
        """
        Separating pooled artifacts.
        i1 -> o1, o2
        i2 -> o3, o4
        i3 -> o5, o6
        """

        expected_input_map = {
                "i1": set(["o1", "o2"]),
                "i2": set(["o3", "o4"]),
                "i3": set(["o5", "o6"])
            }

        expected_output_map = {
                "o1": set(["i1"]),
                "o2": set(["i1"]),
                "o3": set(["i2"]),
                "o4": set(["i2"]),
                "o5": set(["i3"]),
                "o6": set(["i3"])
            }

        self._validate_expected_output_to_parsed_xml(UNPOOLING_XML, expected_input_map, expected_output_map)

    def test_simple(self):
        """
        Standard one to one mapping.
        i1 -> r1
        i2 -> r2
        i3 -> r3
        """

        expected_input_map = {
                "i1": set(["o1"]),
                "i2": set(["o2"]),
                "i3": set(["o3"])
            }

        expected_output_map = {
                "o1": set(["i1"]),
                "o2": set(["i2"]),
                "o3": set(["i3"])
            }

        self._validate_expected_output_to_parsed_xml(ONE_TO_ONE_MAPPING_XML, expected_input_map, expected_output_map)

    def test_no_outputs(self):
        """
        Input artifacts only, no PerAllInputs result files.
        i1 ->
        i2 ->
        i3 ->
        """

        expected_input_map = {
                "i1": set(),
                "i2": set(),
                "i3": set()
            }

        expected_output_map = {}

        self._validate_expected_output_to_parsed_xml(NO_OUTPUTS_XML, expected_input_map, expected_output_map)

    def test_all_result_file_output_only(self):
        """
        Artifacts with no outputs, shared result file
        i1 ->
        i2 ->
        i3 ->
           -> r1
        """
        expected_input_map = {
                "i1": set(),
                "i2": set(),
                "i3": set()
            }

        expected_output_map = {}

        expected_shared_outputs = ["r1"]

        self._validate_expected_output_to_parsed_xml(PER_ALL_INPUT_OUTPUT_ONLY, expected_input_map, expected_output_map, expected_shared_outputs)

    def test_pooling(self):

        expected_input_map = {
                "i1": set(["a1"]),
                "i2": set(["a1"]),
                "i3": set(["a2"]),
                "i4": set(["a2"])
            }

        expected_output_map = {
                "a1": set(["i1", "i2"]),
                "a2": set(["i3", "i4"])
            }

        expected_shared_outputs = ["rf1"]

        self._validate_expected_output_to_parsed_xml(POOLING_XML, expected_input_map, expected_output_map, expected_shared_outputs)

    def _validate_expected_output_to_parsed_xml(self, xml_string, expected_input_map, expected_output_map, expected_shared_outputs=list()):

        # Parse the xml into a StepDetails object
        details = self.element_from_xml(StepDetails, xml_string, step=None)

        # Verify that our input and output keyed dictionaries look like our expected dictionary input
        self.assertEqual(self.artifact_dict_to_limsids_dict(details.iomaps_input_keyed()), expected_input_map)
        self.assertEqual(self.artifact_dict_to_limsids_dict(details.iomaps_output_keyed()), expected_output_map)

        # Verify that the input and output names match and there are no extra or missing names
        input_names = expected_input_map.keys()
        self._verify_names(details.inputs, input_names)

        output_names = expected_output_map.keys()
        self._verify_names(details.outputs, output_names)

        # Check that the iomaps look like we expect them too
        self._verify_expected_input_map(details, expected_input_map)

        shared_output_ids = map(lambda output: output.limsid, details.shared_outputs)
        self.assertEqual(set(shared_output_ids), set(expected_shared_outputs), "Unexpected shared outputs.")

    def _verify_expected_input_map(self, details, expected_input_map):
        # Make sure that the input keyed io map matches our expected input keyed map
        self.assertEqual(self.artifact_dict_to_limsids_dict(details.iomaps_input_keyed()), expected_input_map)

        # Verify that the individual io maps have the expected elements
        for iomap in details.iomaps:
            output_id_set = set([o.limsid for o in iomap.outputs])
            for input_artifact in iomap.inputs:
                self.assertTrue(input_artifact.limsid in expected_input_map, ("Input %s not found in expected map." % input_artifact.limsid))
                self.assertEqual(output_id_set, expected_input_map[input_artifact.limsid], ("Input %s had unexpected outputs." % input_artifact.limsid))

    def _verify_names(self, artifacts, expected_names):

        all_lims_ids = set(map(lambda a: a.limsid, artifacts))

        # Make sure all expected names are there
        self.assertEqual(set(expected_names), set(all_lims_ids), msg="Artifact names do not match expected list.")

        # Make sure the expected number are there
        self.assertEqual(len(artifacts), len(expected_names), msg="Unexpected number of artifacts: %r != %r." % (expected_names, all_lims_ids))

ONE_TO_ONE_MAPPING_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="http://qalocal/api/v2/steps/24-2974/details">
    <step uri="http://qalocal/api/v2/steps/24-2974" rel="steps"/>
    <configuration uri="http://qalocal/api/v2/configuration/protocols/252/steps/554">One to One Mapping</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A20PA1" limsid="i1"/>
            <output uri="http://qalocal/api/v2/artifacts/2-9370" output-generation-type="PerInput" type="Analyte" limsid="o1"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A19PA1" limsid="i2"/>
            <output uri="http://qalocal/api/v2/artifacts/2-9369" output-generation-type="PerInput" type="Analyte" limsid="o2"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A18PA1" limsid="i3"/>
            <output uri="http://qalocal/api/v2/artifacts/2-9368" output-generation-type="PerInput" type="Analyte" limsid="o3"/>
        </input-output-map>
    </input-output-maps>
    <fields/>
</stp:details>
"""


NO_OUTPUTS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="http://qalocal/api/v2/steps/24-2974/details">
    <step uri="http://qalocal/api/v2/steps/24-2974" rel="steps"/>
    <configuration uri="http://qalocal/api/v2/configuration/protocols/252/steps/554">No Outputs</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A20PA1" limsid="i1"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A19PA1" limsid="i2"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A18PA1" limsid="i3"/>
        </input-output-map>
    </input-output-maps>
    <fields/>
</stp:details>
"""

PER_ALL_INPUT_OUTPUT_ONLY = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="http://qalocal/api/v2/steps/24-2974/details">
    <step uri="http://qalocal/api/v2/steps/24-2974" rel="steps"/>
    <configuration uri="http://qalocal/api/v2/configuration/protocols/252/steps/554">Shared Output Only</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A20PA1" limsid="i1"/>
            <output uri="https://qalocal/api/v2/artifacts/92-12330" output-generation-type="PerAllInputs" type="ResultFile" limsid="r1"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A19PA1" limsid="i2"/>
            <output uri="https://qalocal/api/v2/artifacts/92-12330" output-generation-type="PerAllInputs" type="ResultFile" limsid="r1"/>
        </input-output-map>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A18PA1" limsid="i3"/>
            <output uri="https://qalocal/api/v2/artifacts/92-12330" output-generation-type="PerAllInputs" type="ResultFile" limsid="r1"/>
        </input-output-map>
    </input-output-maps>
    <fields/>
</stp:details>
"""

UNPOOLING_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/24-20712/details">
    <step uri="https://qalocal/api/v2/steps/24-20712" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/211/steps/542">Unpooling QC</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65725" limsid="i1"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65739" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65725" limsid="i1"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65740" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o2"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65724" limsid="i2"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65738" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o3"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65724" limsid="i2"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65737" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o4"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65719" limsid="i3"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65736" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o5"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-65719" limsid="i3"/>
            <output uri="https://qalocal/api/v2/artifacts/92-65735" output-generation-type="PerReagentLabel" type="ResultFile" limsid="o6"/>
        </input-output-map>
    </input-output-maps>
    <fields/>
</stp:details>
"""

POOLING_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="https://qalocal/api/v2/steps/122-20527/details">
    <step uri="https://qalocal/api/v2/steps/122-20527" rel="steps"/>
    <configuration uri="https://qalocal/api/v2/configuration/protocols/251/steps/551">Library Pooling</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64481" limsid="i4"/>
            <output uri="https://qalocal/api/v2/artifacts/2-64557" output-generation-type="PerAllInputs" type="Analyte" limsid="a2"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64480" limsid="i3"/>
            <output uri="https://qalocal/api/v2/artifacts/2-64557" output-generation-type="PerAllInputs" type="Analyte" limsid="a2"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64479" limsid="i2"/>
            <output uri="https://qalocal/api/v2/artifacts/2-64556" output-generation-type="PerAllInputs" type="Analyte" limsid="a1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64478" limsid="i1"/>
            <output uri="https://qalocal/api/v2/artifacts/2-64556" output-generation-type="PerAllInputs" type="Analyte" limsid="a1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64481" limsid="i4"/>
            <output uri="https://qalocal/api/v2/artifacts/92-64555" output-generation-type="PerAllInputs" type="ResultFile" limsid="rf1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64480" limsid="i3"/>
            <output uri="https://qalocal/api/v2/artifacts/92-64555" output-generation-type="PerAllInputs" type="ResultFile" limsid="rf1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64479" limsid="i2"/>
            <output uri="https://qalocal/api/v2/artifacts/92-64555" output-generation-type="PerAllInputs" type="ResultFile" limsid="rf1"/>
        </input-output-map>
        <input-output-map>
            <input uri="https://qalocal/api/v2/artifacts/2-64478" limsid="i1"/>
            <output uri="https://qalocal/api/v2/artifacts/92-64555" output-generation-type="PerAllInputs" type="ResultFile" limsid="rf1"/>
        </input-output-map>
    </input-output-maps>
</stp:details>
"""
