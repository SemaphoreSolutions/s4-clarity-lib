# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from collections import defaultdict

from ._internal import ClarityElement


class IOMapsMixin(ClarityElement):
    """
    Parse the StepDetails or Process object,
    https://www.genologics.com/files/permanent/API/latest/rest.version.steps.limsid.details.html#GET
    https://www.genologics.com/files/permanent/API/latest/rest.version.processes.html#GET
    to prepare a list of inputs and outputs for each step/process.

    :ivar list[IOMap] iomaps:
    :ivar list[Artifact] inputs:
    :ivar list[Artifact] outputs:
    :ivar list[Artifact] shared_outputs:
    :ivar dict[Artifact, list[Artifact]] input_keyed_lookup:
    :ivar dict[Artifact, list[Artifact]] output_keyed_lookup:
    """

    IOMAPS_XPATH = None
    IOMAPS_OUTPUT_TYPE_ATTRIBUTE = None

    def __init__(self, *args, **kwargs):
        super(IOMapsMixin, self).__init__(*args, **kwargs)

        self.xml_root  # force population of xml_root, which will initialize lists

    def _init_lists(self):
        self.input_keyed_lookup = {}
        self.output_keyed_lookup = defaultdict(list)
        self.iomaps = []
        shared_output_set = set()
        io_map_nodes = self.xml_findall(self.IOMAPS_XPATH)
        shared_result_file_type = self._get_iomaps_shared_result_file_type()
        for io_map_node in io_map_nodes:

            input_artifact, output_artifact, artifact_type, generation_type = self._get_node_artifacts(io_map_node)

            # If we have not seen this input yet, store it to the input lookup dict.
            # This step builds up our input artifact list and, if there are no per-artifact outputs
            # this is the only place that inputs are recorded.
            if input_artifact not in self.input_keyed_lookup:
                self.input_keyed_lookup[input_artifact] = []

            if output_artifact is not None:
                # Remove all shared result files
                if generation_type == "PerAllInputs" and artifact_type == shared_result_file_type:
                    shared_output_set.add(output_artifact)
                else:
                    # Save the output to its input lookup
                    self.input_keyed_lookup[input_artifact].append(output_artifact)

                    # Save the input to the output's lookup
                    self.output_keyed_lookup[output_artifact].append(input_artifact)

        # If any of the input lists have more than one item we are in a pooling step.
        # There are no steps that will have multiple inputs AND multiple outputs.
        is_pooling = any(len(inputs) > 1 for inputs in self.output_keyed_lookup.values())
        if is_pooling:
            # We are pooling so map multiple inputs to a single output
            self.iomaps = [IOMap(input_artifacts, [output_artifact]) for output_artifact, input_artifacts in
                           self.output_keyed_lookup.items()]
        else:
            # Regular mapping, allow for one to one or replicate generation
            self.iomaps = [IOMap([input_artifact], output_artifacts) for input_artifact, output_artifacts in
                           self.input_keyed_lookup.items()]

        # Prepare our artifact lists
        self.inputs = list(self.input_keyed_lookup)
        self.outputs = list(self.output_keyed_lookup)
        self.shared_outputs = list(shared_output_set)

    def _get_iomaps_shared_result_file_type(self):
        """
        Get the name of the shared result file type that is used in iomap output link nodes
        :rtype: str
        :return: the name
        """
        raise Exception("Classes using the IOMapsMixin must override the _get_iomaps_shared_result_file_type method.")

    def _get_node_artifacts(self, io_map_node):
        """
        Returns the input and output artifacts for a io map node as well as the artifact type and generation_type
        of the output
        :return :type (Artifact, Artifact, String, String)
        """

        # There will always be an input artifact
        input_node = io_map_node.find('input')
        input_artifact = self.lims.artifacts.from_link_node(input_node)

        output_node = io_map_node.find('output')
        if output_node is None:
            return input_artifact, None, None, None

        output_artifact = self.lims.artifacts.from_link_node(output_node)

        artifact_type = output_node.get(self.IOMAPS_OUTPUT_TYPE_ATTRIBUTE)

        generation_type = output_node.get("output-generation-type")

        return input_artifact, output_artifact, artifact_type, generation_type

    def iomaps_input_keyed(self):
        """
        :return: a mapping of input -> outputs.
        :rtype: dict[Artifact, list[Artifact]]
        """
        return self.input_keyed_lookup

    def iomaps_output_keyed(self):
        """
        :return: a mapping of output -> inputs.
        :rtype: dict[Artifact, list[Artifact]]
        """
        return self.output_keyed_lookup

    @property
    def xml_root(self):
        return super(IOMapsMixin, self).xml_root

    @xml_root.setter
    def xml_root(self, root_node):
        super(IOMapsMixin,type(self)).xml_root.__set__(self, root_node)

        if root_node is not None:
            # initialize lists from new xml
            self._init_lists()


class IOMap(object):
    """
    :ivar inputs: list[Artifact]
    :ivar outputs: list[Artifact]
    """
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    @property
    def output(self):
        """
        :type: Artifact
        :raise Exception: If there are multiple output artifacts
        """
        if len(self.outputs) > 1:
            raise Exception("Too many outputs (%d) to get single output" % len(self.outputs))
        return self.outputs[0]

    @property
    def input(self):
        """
        :type: Artifact
        :raise Exception: If there are multiple input artifacts
        """
        if len(self.inputs) > 1:
            raise Exception("Too many inputs (%d) to get single input" % len(self.inputs))
        return self.inputs[0]
