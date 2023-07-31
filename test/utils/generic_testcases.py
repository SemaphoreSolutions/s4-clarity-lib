# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from unittest import TestCase

from s4.clarity import ETree


class LimsTestCase(TestCase):
    @staticmethod
    def element_from_xml(element_class, xml, **extra_kwargs):
        try:
            return element_class(
                lims=FakeLims(),
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


class FakeLims:
    def __init__(self):
        self.artifacts = FakeFactory()
        self.samples = FakeFactory()
        self.steps = FakeFactory()

    def factory_for(self, element_type):
        return self.artifacts


class FakeFactory:
    def __init__(self):
        self.instances = {}

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
