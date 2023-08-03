from s4.clarity.container import Container
from s4.clarity.test.generic_testcases import LimsTestCase


class TestContainer(LimsTestCase):
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
