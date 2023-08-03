# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import logging

log = logging.getLogger(__name__)

ROW_ORDER = "row"
COLUMN_ORDER = "column"


def column_order_sort_keys(artifact):
    """
    Provide container position sort-keys for the sorted function based on column-major order

    Usage example::

        sorted_outputs = sorted(self.outputs, key=row_order_sort_keys)

    :type artifact: s4.clarity.Artifact
    :rtype: tuple(str|int, str|int)
    """
    location_pieces = _split_location_pieces(artifact.location_value)
    return location_pieces[1], location_pieces[0]


def row_order_sort_keys(artifact):
    """
    Provide container position sort-keys for the sorted function based on row-major order

    Usage example::

        sorted_outputs = sorted(self.outputs, key=row_order_sort_keys)

    :type artifact: s4.clarity.Artifact
    :rtype: tuple(str|int, str|int)
    """
    location_pieces = _split_location_pieces(artifact.location_value)
    return location_pieces[0], location_pieces[1]


def _split_location_pieces(location_value):
    location_pieces = location_value.split(":")
    return [_parse_location_piece(piece) for piece in location_pieces]


def _parse_location_piece(location_piece):
    if location_piece.isdigit():
        return int(location_piece)
    else:
        return location_piece


def place_plate_to_plate_match_wells(step, input_container, output_container):
    """
    Places samples in the input_container in the output_container at
    the same well location.
    Plates do not have to be the same dimensions, but artifacts placed
    at invalid wells will not be accepted by Clarity.

    To submit these changes you will need to call step.placements.post_and_parse() after.
    :param step: The step that the placement is being done for
    :param input_container: Container with artifacts to place in the output container
    :param output_container: Container that will be populated with artifacts.
    """
    for io_map in step.details.iomaps:
        if io_map.input.container == input_container:
            step.placements.create_placement(io_map.output, output_container, io_map.input.location_value)


def auto_place_artifacts(step, artifacts, order=ROW_ORDER):
    """
    Places the artifacts provided, in the order provided, to selected_containers in the step.

    :type step: Step
    :type artifacts: list[Artifact]
    :type order: str
    """

    step.placements.clear_placements()
    output_iterator = iter(artifacts)
    number_outputs = len(artifacts)
    number_placed_outputs = 0

    # Note: This will not create new containers, only use the ones currently provided.
    containers = step.placements.selected_containers
    for container in containers:
        if order == ROW_ORDER:
            wells = container.container_type.row_major_order_wells()
        elif order == COLUMN_ORDER:
            wells = container.container_type.column_major_order_wells()
        else:
            raise Exception("Auto Place Error - Unrecognized order type '%s'" % order)

        for well in wells:
            output = next(output_iterator, None)
            if output is None:
                break

            log.debug("Placing %s in well %s of container %s", output, well, container.name)
            step.placements.create_placement(output, container, well)
            number_placed_outputs += 1

        # we're out of either outputs or wells before if below
        if number_placed_outputs == number_outputs:
            # Submit and return
            step.placements.post_and_parse()
            step.refresh()
            return

            # we're out of wells, continue to next container

    # we're out of containers
    raise Exception("Auto Place Error - Insufficient containers for artifacts.")
