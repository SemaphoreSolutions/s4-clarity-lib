# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging

log = logging.getLogger(__name__)


def copy_from_input_to_output(step, udf_names):
    """
    Copies a set of UDFs from the inputs of a step to its outputs.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    Will throw an exception if there are more than one input per output.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = _keyed_io_maps_to_array(step.details.iomaps_input_keyed())
    return _copy(pairs, udf_names)


def copy_from_output_to_input(step, udf_names):
    """
    Copies a set of UDFs from the outputs of a step to its inputs, one to one.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    Will throw an exception if there are more than one input per output or more than one output per input.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = _keyed_io_maps_to_array(step.details.iomaps_output_keyed())
    return _copy(pairs, udf_names)


def _keyed_io_maps_to_array(keyed_io_maps):
    """
    Prepares an array of keyed artifact to value artifacts
    :param dict[Artifact:list(Artifact)]: Artifact to list of Artifact dictionary
    :return: list[(Artifact, Artifact)]
    """
    pairs = []
    for key_artifact in keyed_io_maps:
        for related_artifact in keyed_io_maps[key_artifact]:
            pairs.append((key_artifact, related_artifact))
    return pairs


def copy_from_input_to_sample(step, udf_names):
    """
    Copies a set of UDFs from the inputs of a step to each input's sample.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = [
        (artifact, artifact.sample) for artifact in step.details.inputs
    ]

    return _copy(pairs, udf_names)


def copy_from_output_to_sample(step, udf_names):
    """
    Copies a set of UDFs from the outputs of a step to each output's sample.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = [
        (artifact, artifact.sample) for artifact in step.details.outputs
    ]

    return _copy(pairs, udf_names)


def copy_from_sample_to_input(step, udf_names):
    """
    Copies a set of UDFs to the inputs of a step from each input's sample.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = [
        (artifact.sample, artifact) for artifact in step.details.inputs
    ]

    return _copy(pairs, udf_names)


def copy_from_sample_to_output(step, udf_names):
    """
    Copies a set of UDFs to the outputs of a step from each output's sample.
    - Supply a list of UDFs if the source and destination names are the same.
    - Supply a dictionary (source name to destination name) if they differ.

    If the UDF is not present on the source, it is skipped.

    :type step: s4.clarity.Step
    :type udf_names: list[str]|dict[str:str]
    """
    pairs = [
        (artifact.sample, artifact) for artifact in step.details.outputs
    ]

    return _copy(pairs, udf_names)


def _copy(pairs, udf_names):
    """
    Does the copy operation.

    :type pairs: list[(Artifact, Artifact)]
    :type udf_names: list[str]|dict[str:str]
    """
    for source, destination in pairs:
        if type(udf_names) == dict:
            for (source_udf, destination_udf) in udf_names.items():
                if source_udf in source:
                    log.info("Copying UDF '%s' on %s to UDF '%s' on %s", source_udf, source, destination_udf, destination)
                    destination[destination_udf] = source[source_udf]
        else:
            for udf_name in udf_names:
                if udf_name in source:
                    log.info("Copying UDF '%s' from %s to %s", udf_name, source, destination)
                    destination[udf_name] = source[udf_name]