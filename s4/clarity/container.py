# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import WrappedXml, ClarityElement, FieldsMixin
from s4.clarity._internal.props import subnode_link, subnode_property, subnode_element
from s4.clarity import types, lazy_property


class ContainerDimension(WrappedXml):
    is_alpha = subnode_property("is-alpha", types.BOOLEAN)
    offset = subnode_property("offset", types.NUMERIC)  # type: float
    size = subnode_property("size", types.NUMERIC)  # type: float

    @lazy_property
    def dimension_range(self):
        """
        List of the labels for the given dimension

        :return: list[int]|list[str]
        """

        # Cast these to integers from floats to avoid deprecation warnings from range.
        start = int(self.offset)
        end = int(self.offset + self.size)

        if not self.is_alpha:
            return list(range(start, end))
        else:
            return list(map(chr, range(65 + start, 65 + end)))

    def as_index(self, label):
        if label.isdigit():
            return int(label) - int(self.offset)
        else:
            return ord(label[0]) - 65 - int(self.offset)

    def as_label(self, index):
        if self.is_alpha:
            return chr(65 + index + int(self.offset))
        else:
            return str(index + int(self.offset))


class ContainerType(ClarityElement):
    """
    A class to handle container types, with helper functions to create and encode well positions
    For the purposes of this class, the y-dimension is considered the columns, and the x-dimension is considered the rows.
    """
    UNIVERSAL_TAG = "{http://genologics.com/ri/containertype}container-type"

    is_tube = subnode_property("is-tube", types.BOOLEAN)  # type: bool
    x_dimension = subnode_element(ContainerDimension, "x-dimension")  # type: ContainerDimension
    y_dimension = subnode_element(ContainerDimension, "y-dimension")  # type: ContainerDimension

    def well_to_rc(self, well):
        """
        Converts a Clarity well position to the zero based index of the row and column.

        Example::

             'B:4' -> (1, 3)

        :param well: A Clarity formatted well position
        :type well: str
        :return: The zero based index of the row and the column.
        :rtype: tuple[int]
        """
        location_pieces = well.split(":")

        return self.y_dimension.as_index(location_pieces[0]), self.x_dimension.as_index(location_pieces[1])

    def rc_to_well(self, rc):
        """
        Converts a zero based index of the row and column to a Clarity well position.

        Example::

             (1, 3) -> 'B:4'

        :param rc: The zero based index of the row and the column.
        :type rc: tuple[int]
        :return: A Clarity formatted well position
        :rtype: str
        """
        return "%s:%s" % (self.y_dimension.as_label(rc[0]), self.x_dimension.as_label(rc[1]))

    def row_major_order_wells(self):
        """
        Returns wells in the container type in row major order.
        This will return the wells ordered: ["y1:x1", "y1:x2", "y1:x3", [...], "y1,xn", "y2:x1", "y2:x2", [...]]

        Unavailable wells are omitted.

        :rtype: list[str]
        """
        l = []
        for y in self.y_dimension.dimension_range:
            for x in self.x_dimension.dimension_range:
                well_name = "%s:%s" % (str(y), str(x))

                if well_name not in self.unavailable_wells:
                    l.append(well_name)
        return l

    def column_major_order_wells(self):
        """
        Returns wells in the container type in column major order.
        This will return the wells ordered: ["y1:x1", "y2:x1", "y3:x1", [...], "yn:x1", "y1:x2", "y2:x2", [...]]

        Unavailable wells are omitted.

        :rtype: list[str]
        """
        l = []
        for x in self.x_dimension.dimension_range:
            for y in self.y_dimension.dimension_range:
                well_name = "%s:%s" % (str(y), str(x))

                if well_name not in self.unavailable_wells:
                    l.append(well_name)
        return l

    @lazy_property
    def unavailable_wells(self):
        """
        :type: set[str]
        """
        unavailable_well_nodes = self.xml_findall("unavailable-well")
        return set(node.text for node in unavailable_well_nodes)

    @lazy_property
    def total_capacity(self):
        """
        :type: int
        """
        return len(self.x_dimension.dimension_range) * len(self.y_dimension.dimension_range) - len(self.unavailable_wells)

    def row_order_wells(self):
        """
        :deprecated: use :class:`ContainerType.row_major_order_wells()` instead.
        """
        return self.row_major_order_wells()

    def column_order_wells(self):
        """
        :deprecated: use :class:`ContainerType.column_major_order_wells()` instead.
        """
        return self.column_major_order_wells()

    def x_dimension_range(self):
        """
        :deprecated: use :class:`ContainerType.x_dimension.dimension_range` instead
        """
        return self.x_dimension.dimension_range

    def y_dimension_range(self):
        """
        :deprecated: use :class:`ContainerType.y_dimension.dimension_range` instead
        """
        return self.y_dimension.dimension_range


class Container(FieldsMixin, ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/container}container"
    ATTACH_TO_NAME = "Container"

    container_type = subnode_link(ContainerType, "type", attributes=('name', 'uri'))
    occupied_wells = subnode_property("occupied-wells", typename=types.NUMERIC, readonly=True)
    state = subnode_property("state", typename=types.STRING, readonly=True)

    @property
    def type_name(self):
        """
        Read-only shortcut to containertype name, which we know without doing another GET.

        :type: str
        """
        typenode = self.xml_find('./type')
        return typenode.get('name')

    @property
    def placements(self):
        """
        Dict of string "Y:X" -> Artifacts.

        :type: dict[str, Artifact]
        """
        return self.xml_all_as_dict("placement",
                                    lambda n: n.find("value").text,  # key
                                    lambda n: self.lims.artifacts.from_link_node(n)  # value
                                    )

    def artifact_at(self, well):
        """
        :param well: String matching "Y:X" where Y is a column index and X is a row index.
            The string may use letters or numbers depending on the container type.
        :type well: str

        :rtype: Artifact or None
        """
        try:
            return self.placements[well]
        except KeyError:
            raise KeyError("Container '%s' has no artifact at '%s'." % (self.name, well))
