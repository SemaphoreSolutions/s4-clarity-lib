# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from collections import defaultdict


def get_parent_artifacts(lims, artifacts):
    """
    Helper method to get the parent artifacts keyed to the supplied artifacts

    :param LIMS lims:
    :param list[Artifact] artifacts: The artifacts to get parent artifacts for
    :rtype: dict[Artifact, list[Artifact]]
    """
    artifact_to_parent_artifacts = defaultdict(list)
    artifacts_to_batch_fetch = []

    for artifact in artifacts:
        if artifact.parent_step:
            # Ugly list comprehension that covers pooled inputs and replicates
            artifact_to_parent_artifacts[artifact] = [input_artifact for iomap in artifact.parent_step.details.iomaps
                                                      for input_artifact in iomap.inputs
                                                      if any(output.limsid == artifact.limsid for output in iomap.outputs)]
            artifacts_to_batch_fetch += artifact_to_parent_artifacts[artifact]
        else:
            # Without a parent_step, we've reached the end of the artifact history
            artifact_to_parent_artifacts[artifact] = []

    if artifact_to_parent_artifacts:
        lims.artifacts.batch_fetch(set(artifacts_to_batch_fetch))

    return artifact_to_parent_artifacts


def get_udfs_from_artifacts_or_ancestors(lims, artifacts_to_get_udf_from, required_udfs=None, optional_udfs=None):
    """
    Walks the genealogy for each artifact in the artifacts_to_get_udf_from list and gets the value for udf_name from the
    supplied artifact, or its first available ancestor that has a value for the UDF.
    NOTE: The method will stop the search upon reaching any pooling step.

    :param LIMS lims:
    :param list[Artifact] artifacts_to_get_udf_from: the list of artifacts whose ancestors should be inspected for the udf. Passed
        down recursively until all artifacts have been satisfied.
    :param list[str] required_udfs: The list of UDFs that *must* be found. Exception will be raised otherwise.
    :param list[str] optional_udfs: The list of UDFs that *can* be found, but do not need to be.
    :rtype: dict[s4.clarity.Artifact, dict[str, str]]
    :raises UserMessageException: if values can not be retrieved for all required_udfs for all of the provided artifacts
    """
    if not required_udfs and not optional_udfs:
        raise Exception("The get_udfs_from_artifacts_or_ancestors method must be called with at least one "
                        "of the required_udfs or optional_udfs parameters.")

    required_udfs = required_udfs or []
    optional_udfs = optional_udfs or []

    # Assemble the dictionaries for the internal methods
    ancestor_artifact_to_original_artifact = {}
    original_artifact_to_udfs = {}

    for artifact in artifacts_to_get_udf_from:
        ancestor_artifact_to_original_artifact[artifact] = [artifact]
        original_artifact_to_udfs[artifact] = {}

        for name in (required_udfs + optional_udfs):
            original_artifact_to_udfs[artifact][name] = artifact.get(name, None)

    artifacts_to_udfs = _get_udfs_from_ancestors_internal(
        lims, ancestor_artifact_to_original_artifact, original_artifact_to_udfs)

    if required_udfs:
        _validate_required_ancestor_udfs(artifacts_to_udfs, required_udfs)

    return artifacts_to_udfs


def _validate_required_ancestor_udfs(artifacts_to_udfs, required_udfs):
    """
    Validates that all items in the artifacts_to_udfs dict have values for the required_udfs
    :type artifacts_to_udfs: dict[s4.clarity.Artifact, dict[str, str]]
    :type required_udfs: list[str]
    :raises UserMessageException: if any artifact is missing any of the required_udfs
    """
    artifacts_missing_udfs = set()
    missing_udfs = set()

    for artifact, udf_name_to_value in artifacts_to_udfs.items():
        for required_udf in required_udfs:
            if udf_name_to_value.get(required_udf) in ["", None]:
                artifacts_missing_udfs.add(artifact.name)
                missing_udfs.add(required_udf)

    if artifacts_missing_udfs:
        raise Exception("Could not get required values for udf(s) '%s' from ancestors of artifact(s) '%s'." %
                        ("', '".join(missing_udfs), "', '".join(artifacts_missing_udfs)))


def _get_udfs_from_ancestors_internal(lims, current_artifacts_to_original_artifacts, original_artifacts_to_udfs):
    """
    Recursive method that gets parent artifacts, and searches them for any udfs that have not yet been filled in
    :type lims: s4.clarity.LIMS
    :type current_artifacts_to_original_artifacts: dict[s4.clarity.Artifact: list[s4.clarity.Artifact]]
    :param current_artifacts_to_original_artifacts: dict of the currently inspected artifact to the original artifact.
    :type original_artifacts_to_udfs: dict[s4.clarity.Artifact, dict[str, str]]
    :param original_artifacts_to_udfs: dict of the original artifacts to their ancestors' UDF values, which will
    get filled in over the recursive calls of this method.
    :rtype: dict[s4.clarity.Artifact, dict[str, Any]]
    """
    current_artifacts = list(current_artifacts_to_original_artifacts)
    current_artifacts_to_parent_artifacts = get_parent_artifacts(lims, list(current_artifacts_to_original_artifacts))

    # Initialize the 'next to search' dict
    next_search_artifacts_to_original_artifacts = defaultdict(list)

    for current_artifact in current_artifacts:

        if not current_artifacts_to_parent_artifacts[current_artifact]:
            # The end of the genealogy has been reached for this artifact
            continue

        if current_artifact.parent_step.pooling is not None:
            # Stop looking when we reach a step with pooled inputs, as ancestor artifacts would likely contain multiple
            # values for the UDFs in question
            continue

        # Can now get a single parent artifact with confidence, as validated it
        current_artifact_parent = current_artifacts_to_parent_artifacts[current_artifact][0]

        for original_artifact in current_artifacts_to_original_artifacts[current_artifact]:
            continue_searching = False

            for udf_name, udf_value in original_artifacts_to_udfs[original_artifact].items():
                # Don't overwrite values that have already been found
                if udf_value is not None:
                    continue

                found_value = current_artifact_parent.get(udf_name, None)

                if found_value is None:
                    continue_searching = True
                    continue

                original_artifacts_to_udfs[original_artifact][udf_name] = found_value

            if continue_searching:
                next_search_artifacts_to_original_artifacts[current_artifact_parent].append(original_artifact)

    if next_search_artifacts_to_original_artifacts:
        return _get_udfs_from_ancestors_internal(lims, next_search_artifacts_to_original_artifacts, original_artifacts_to_udfs)

    return original_artifacts_to_udfs
