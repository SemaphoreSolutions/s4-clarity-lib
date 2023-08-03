import string

from s4.clarity.container import ContainerType, Container
from s4.clarity.test.generic_testcases import LimsTestCase


class TestContainer(LimsTestCase):
    def test_tube_container_type(self):
        container_type = self.element_from_xml(ContainerType, TUBE_CONTAINER_TYPE)

        self.assertTrue(container_type.is_tube)
        self.assertEqual(container_type.total_capacity, 1)
        self.assertEqual(len(container_type.column_major_order_wells()), 1)
        self.assertEqual(container_type.column_major_order_wells()[0], "1:1")

    def test_96_well_plate_container_type(self):
        container_type = self.element_from_xml(ContainerType, PLATE_96_WELL_CONTAINER_TYPE_XML)

        self.assertFalse(container_type.is_tube)
        self.assertEqual(container_type.total_capacity, 96)
        self.assertEqual(len(container_type.column_major_order_wells()), 96)
        self.assertEqual(len(container_type.row_major_order_wells()), 96)

        # Check the column order is what we expect
        self.assertEqual(container_type.column_major_order_wells()[0], "A:1")
        self.assertEqual(container_type.column_major_order_wells()[1], "B:1")
        self.assertEqual(container_type.column_major_order_wells()[94], "G:12")
        self.assertEqual(container_type.column_major_order_wells()[95], "H:12")

        # Check the row order is what we expect
        self.assertEqual(container_type.row_major_order_wells()[0], "A:1")
        self.assertEqual(container_type.row_major_order_wells()[1], "A:2")
        self.assertEqual(container_type.row_major_order_wells()[94], "H:11")
        self.assertEqual(container_type.row_major_order_wells()[95], "H:12")

        x_dimension = container_type.x_dimension
        self.assertEqual(x_dimension.offset, 1)
        self.assertEqual(x_dimension.size, 12)
        self.assertFalse(x_dimension.is_alpha)
        self.assertEqual(x_dimension.dimension_range, list(range(1, 13)))
        self.assertEqual(x_dimension.as_index("2"), 1)
        self.assertEqual(x_dimension.as_label(1), "2")

        y_dimension = container_type.y_dimension
        self.assertEqual(y_dimension.offset, 0)
        self.assertEqual(y_dimension.size, 8)
        self.assertTrue(y_dimension.is_alpha)
        self.assertEqual(y_dimension.dimension_range, list(string.ascii_uppercase[0:8]))
        self.assertEqual(y_dimension.as_index("B"), 1)
        self.assertEqual(y_dimension.as_label(1), "B")

        self.assertEqual(container_type.well_to_rc("B:5"), (1, 4))
        self.assertEqual(container_type.rc_to_well((1, 4)), "B:5")

    def test_well_ordering_and_unavailable_wells(self):
        container_type = self.element_from_xml(ContainerType, PLATE_ORDERING_TEST_TYPE_XML)
        self.assertEqual(container_type.unavailable_wells, {"A:2", "B:1"})
        expected_column_major_ordering = [
            "A:1",
            "C:1",
            "B:2",
            "C:2",
            "A:3",
            "B:3",
            "C:3",
        ]
        self.assertEqual(container_type.column_major_order_wells(), expected_column_major_ordering)
        expected_row_major_ordering = [
            "A:1",
            "A:3",
            "B:2",
            "B:3",
            "C:1",
            "C:2",
            "C:3",
        ]
        self.assertEqual(container_type.row_major_order_wells(), expected_row_major_ordering)


TUBE_CONTAINER_TYPE = """
<ctp:container-type xmlns:ctp="http://genologics.com/ri/containertype" uri="https://qalocal/api/v2/containertypes/2" name="Tube">
    <is-tube>true</is-tube>
    <x-dimension>
        <is-alpha>false</is-alpha>
        <offset>1</offset>
        <size>1</size>
    </x-dimension>
    <y-dimension>
        <is-alpha>false</is-alpha>
        <offset>1</offset>
        <size>1</size>
    </y-dimension>
</ctp:container-type>"""

PLATE_96_WELL_CONTAINER_TYPE_XML = """
<ctp:container-type xmlns:ctp="http://genologics.com/ri/containertype" uri="https://qalocal/api/v2/containertypes/1" name="96 well plate">
    <is-tube>false</is-tube>
    <x-dimension>
        <is-alpha>false</is-alpha>
        <offset>1</offset>
        <size>12</size>
    </x-dimension>
    <y-dimension>
        <is-alpha>true</is-alpha>
        <offset>0</offset>
        <size>8</size>
    </y-dimension>
</ctp:container-type>"""

PLATE_ORDERING_TEST_TYPE_XML = """
<ctp:container-type xmlns:ctp="http://genologics.com/ri/containertype" uri="https://qalocal/api/v2/containertypes/1" name="Ordering Test Plate">
    <is-tube>false</is-tube>
    <unavailable-well>A:2</unavailable-well>
    <unavailable-well>B:1</unavailable-well>
    <x-dimension>
        <is-alpha>false</is-alpha>
        <offset>1</offset>
        <size>3</size>
    </x-dimension>
    <y-dimension>
        <is-alpha>true</is-alpha>
        <offset>0</offset>
        <size>3</size>
    </y-dimension>
</ctp:container-type>"""
