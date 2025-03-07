# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from unittest import TestCase

from s4.clarity import ETree


class FakeLims:
    def __init__(self):
        self.artifacts = FakeFactory()
        self.samples = FakeFactory()
        self.steps = FakeFactory()
        self.instrument_types = FakeFactory()

    def factory_for(self, element_type):
        return self.artifacts


class FakeFactory:
    def __init__(self):
        self.instances = {}

    def get_by_name(self, name):
        o = FakeElement()
        return o

    def from_link_node(self, linknode):
        if linknode is None:
            return None

        uri = linknode.get("uri")
        if uri in self.instances:
            return self.instances[uri]

        o = FakeElement()
        for attr in ("uri", "name", "limsid"):
            v = linknode.get(attr)
            if v is not None:
                setattr(o, attr, v)
        self.instances[uri] = o
        return o

    # Copied directly from Factory
    def from_link_nodes(self, xml_nodes):
        objs = []
        for xml_node in xml_nodes:
            obj = self.from_link_node(xml_node)
            if obj is not None:
                objs.append(obj)
        return objs


    @staticmethod
    def batch_fetch(*args, **kwargs):
        return


class FakeElement:
    def __str__(self):
        return str(self.__dict__)


class LimsTestCase(TestCase):

    @staticmethod
    def get_fake_lims():
        return FakeLims()

    def element_from_xml(self, element_class, xml, **extra_kwargs):
        try:
            return element_class(
                lims=self.get_fake_lims(),
                xml_root=ETree.fromstring(xml),
                **extra_kwargs
            )
        except TypeError as e:
            str(e)
            if "__init__() takes at least" in str(e):
                raise TypeError("Unable to instantiate %s, provide extra args in extra_kwargs. %s"
                                % (element_class.__name__, e))
            else:
                raise e
