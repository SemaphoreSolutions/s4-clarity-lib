# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging

from ._internal import FieldsMixin, ClarityElement
from ._internal.props import subnode_property, subnode_link
from s4.clarity.project import Project
from s4.clarity.artifact import Artifact
from s4.clarity import ETree
from s4.clarity import types

log = logging.getLogger(__name__)


class Sample(FieldsMixin, ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/sample}sample"
    # special tag used for creation posts
    CREATION_TAG = "{http://genologics.com/ri/sample}samplecreation"
    ATTACH_TO_NAME = "Sample"

    date_received = subnode_property("date-received", types.DATE)
    date_completed = subnode_property("date-completed", types.DATE)

    project = subnode_link(Project, "project")

    artifact = subnode_link(Artifact, "artifact")

    @property
    def is_control(self):
        """
        :type: bool
        """
        return self.xml_find('./control-type') is not None

    def set_location(self, container, row, col):
        """
        Sets this artifact's location (usually for sample creation) with
        the given row and column, in the given container.

        :param container: The Sample's container
        :type container: s4.clarity.Container
        :param row: The well position row.
        :type row: str or int
        :param col: The well position column
        :type col: str or int
        :deprecated: Use set_location_coords or set_location_well
        """
        log.warning("Deprecated call: sample.set_location. Use set_location_coords or set_location_well.")
        return self.set_location_coords(container, row, col)

    def set_location_coords(self, container, row, col):
        """
        Sets this artifact's location (usually for sample creation) with
        the given row and column, in the given container.

        Equivalent to set_location_well with the string "<row>:<col>".

        :param container: The Sample's container
        :type container: s4.clarity.Container
        :param row: The well position row.
        :type row: str or int
        :param col: The well position column
        :type col: str or int
        """
        return self.set_location_well(container, '{0}:{1}'.format(row, col))

    def set_location_well(self, container, well):
        """"
        Sets this artifact's location (usually for sample creation) with
        the given well location, in the given container.

        :param container: The Sample's container
        :type container: s4.clarity.Container
        :param well: The well position in the form "<row>:<col>"
        :type well: str
        """
        location_node = self.make_subelement_with_parents("./location")
        ETree.SubElement(location_node, 'value').text = well

        # attach container node, which must have the uri
        ETree.SubElement(location_node, 'container', {'uri': container.uri})
