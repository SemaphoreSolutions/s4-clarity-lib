# Copyright 2023 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import string

from s4.clarity.container import ContainerType, Container
from utils.generic_testcases import LimsTestCase


class TestContainer(LimsTestCase):

    def test_tube_container_type(self):
        container_type = self.element_from_xml(ContainerType, TUBE_CONTAINER_TYPE)

        self.assertTrue(container_type.is_tube)
        self.assertEqual(container_type.total_capacity, 1)
        self.assertEqual(len(container_type.column_order_wells()), 1)
        self.assertEqual(container_type.column_order_wells()[0], "1:1")

    def test_96_well_plate_container_type(self):
        container_type = self.element_from_xml(ContainerType, PLATE_96_WELL_CONTAINER_TYPE_XML)

        self.assertFalse(container_type.is_tube)
        self.assertEqual(container_type.total_capacity, 96)
        self.assertEqual(len(container_type.column_order_wells()), 96)
        self.assertEqual(len(container_type.row_order_wells()), 96)

        # Check the column order is what we expect
        self.assertEqual(container_type.column_order_wells()[0], "A:1")
        self.assertEqual(container_type.column_order_wells()[1], "B:1")
        self.assertEqual(container_type.column_order_wells()[94], "G:12")
        self.assertEqual(container_type.column_order_wells()[95], "H:12")

        # Check the row order is what we expect
        self.assertEqual(container_type.row_order_wells()[0], "A:1")
        self.assertEqual(container_type.row_order_wells()[1], "A:2")
        self.assertEqual(container_type.row_order_wells()[94], "H:11")
        self.assertEqual(container_type.row_order_wells()[95], "H:12")

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

        self.assertEqual(container_type.well_to_rc("B:5"), (1,4))
        self.assertEqual(container_type.rc_to_well((1,4)), "B:5")

    def test_tube_container(self):
        container = self.element_from_xml(Container, TUBE_CONTAINER_FULL_XML)
        self.assertEqual(container.occupied_wells, 1)
        self.assertEqual(container.state, "Populated")
        self.assertEqual(container.type_name, "Tube")
        self.assertEqual(container.placements["1:1"].limsid, "ADM51A2PA1")

    def test_48_well_plate_container(self):
        container = self.element_from_xml(Container, PLATE_48_WELL_CONTAINER_XML)
        self.assertEqual(container.occupied_wells, 22)
        self.assertEqual(container.state, "Populated")
        self.assertEqual(container.type_name, "48 well plate")
        self.assertEqual(len(container.placements), 22)
        self.assertEqual(container.placements["E:2"].limsid, "2-7628")
        self.assertEqual(container.placements["C:1"].limsid, "2-7620")


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

TUBE_CONTAINER_FULL_XML = """
<con:container xmlns:udf="http://genologics.com/ri/userdefined" xmlns:con="http://genologics.com/ri/container" uri="https://qalocal/api/v2/containers/27-2" limsid="27-2">
    <name>27-2</name>
    <type uri="https://qalocal/api/v2/containertypes/2" name="Tube"/>
    <occupied-wells>1</occupied-wells>
    <placement uri="https://qalocal/api/v2/artifacts/ADM51A2PA1" limsid="ADM51A2PA1">
        <value>1:1</value>
    </placement>
    <state>Populated</state>
</con:container>"""

PLATE_48_WELL_CONTAINER_XML = """
<con:container xmlns:udf="http://genologics.com/ri/userdefined" xmlns:con="http://genologics.com/ri/container" uri="https://qalocal/api/v2/containers/27-1438" limsid="27-1438">
    <name>27-1438</name>
    <type uri="https://qalocal/api/v2/containertypes/6" name="48 well plate"/>
    <occupied-wells>22</occupied-wells>
    <placement uri="https://qalocal/api/v2/artifacts/2-7622" limsid="2-7622">
        <value>D:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7615" limsid="2-7615">
        <value>A:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7621" limsid="2-7621">
        <value>D:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7616" limsid="2-7616">
        <value>A:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7630" limsid="2-7630">
        <value>G:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7628" limsid="2-7628">
        <value>E:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7632" limsid="2-7632">
        <value>E:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7618" limsid="2-7618">
        <value>B:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7634" limsid="2-7634">
        <value>E:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7636" limsid="2-7636">
        <value>C:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7631" limsid="2-7631">
        <value>H:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7627" limsid="2-7627">
        <value>H:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7619" limsid="2-7619">
        <value>C:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7629" limsid="2-7629">
        <value>F:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7626" limsid="2-7626">
        <value>G:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7617" limsid="2-7617">
        <value>B:1</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7635" limsid="2-7635">
        <value>F:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7633" limsid="2-7633">
        <value>D:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7625" limsid="2-7625">
        <value>F:2</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7623" limsid="2-7623">
        <value>A:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7624" limsid="2-7624">
        <value>B:3</value>
    </placement>
    <placement uri="https://qalocal/api/v2/artifacts/2-7620" limsid="2-7620">
        <value>C:1</value>
    </placement>
    <state>Populated</state>
</con:container>"""