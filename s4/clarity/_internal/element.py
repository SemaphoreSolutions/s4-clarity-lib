# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import six
from future.utils import python_2_unicode_compatible
import logging
from s4.clarity import ETree
from .lazy_property import lazy_property

log = logging.getLogger(__name__)


class WrappedXml(object):
    def __init__(self, lims, xml_root=None):
        self.lims = lims
        self._xml_root = xml_root

    @property
    def xml_root(self):
        """
        :rtype: ETree.Element
        """
        return self._xml_root

    @xml_root.setter
    def xml_root(self, root_node):
        self._xml_root = root_node

    def xml_findall(self, xpath):
        """
        :type xpath: str
        :rtype: list[ETree.Element]
        """
        return self.xml_root.findall(xpath)

    def xml_find(self, xpath):
        """
        :type xpath: str
        :rtype: ETree.Element
        """
        return self.xml_root.find(xpath)

    def xml_all_as_dict(self, xpath, keylambda, valuelambda):
        """
        Return all found nodes at xpath as a dict, using lambda to set key and value.

        :type xpath: str
        :param xpath: xpath which returns multiple nodes
        :type keylambda: (ETree.Element) -> object
        :type valuelambda: (ETree.Element) -> object
        :rtype: dict
        """
        d = {}
        for node in self.xml_findall(xpath):
            d[keylambda(node)] = valuelambda(node)
        return d

    def get_node_text(self, subnode_name):
        """
        :type subnode_name: str
        :rtype: str
        """
        element = self.xml_find('./' + subnode_name)

        if element is None:
            return None

        return element.text

    def set_subnode_text(self, path, value):
        """
        :type path: str
        :type value: str
        """
        node = self.get_or_create_subnode(path)

        node.text = value

    def get_or_create_subnode(self, path):
        node = self.xml_find(path)
        if node is None:
            parent = self.xml_root
            for node_name in path.split('/'):
                node = parent.find(node_name)
                if node is None:
                    node = ETree.SubElement(parent, node_name)
                parent = node
        return node

    def remove_subnode(self, subnode_name):
        """
        :type subnode_name: str
        """
        node = self.xml_find('./' + subnode_name)

        if node is not None:
            self.xml_root.remove(node)

    def make_subelement_with_parents(self, xpath):
        node = self.xml_root

        if not xpath.startswith("."):
            raise Exception("xpath must start with . to make all subelements.")

        for subelement_name in xpath.split('/')[1:]:
            subnode = node.find("./" + subelement_name)
            if subnode is None:
                subnode = ETree.SubElement(node, subelement_name)
            node = subnode

        return node

    @property
    def xml(self):
        """:rtype: str|bytes"""
        return ETree.tostring(self.xml_root)


class ClarityElement(WrappedXml):
    """
    :ivar ETree.Element xml_root:
    :ivar str|None uri:
    :ivar LIMS lims:
    """

    UNIVERSAL_TAG = None

    def __init__(self, lims, uri=None, xml_root=None, name=None, limsid=None):
        super(ClarityElement, self).__init__(lims, None)
        self.uri = uri
        self._name = name
        self._limsid = limsid

        # use property setter to ensure post-set steps are correctly followed
        self.xml_root = xml_root

    @python_2_unicode_compatible
    def __str__(self):
        if self._xml_root is not None:
            name = self.name
            if name:
                return u"[%s %s (%s)]" % (self.__class__.__name__, self.limsid, name)
            else:
                return u"[%s %s]" % (self.__class__.__name__, self.limsid)
        elif self.uri:
            guessed_limsid = self.uri.split('/')[-1]
            return u"[%s %s, unretrieved]" % (self.__class__.__name__, guessed_limsid)
        else:
            return u"[undefined %s]" % (self.__class__.__name__)

    @property
    def name(self):
        """
        The name of the element instance in Clarity.

        :type: str
        """
        if self._name is None:
            name = self.xml_root.get("name")
            if name is not None:
                self._name = name
            else:
                # use this even if it is None
                self._name = self.get_node_text("name")
        return self._name

    @name.setter
    def name(self, value):
        old_name = self.xml_root.get("name")
        if old_name is not None:
            self.xml_root.set("name", value)
        else:
            self.set_subnode_text("name", value)
        self._name = value

    @property
    def xml_root(self):
        """
        :type: ETree.Element
        """
        if self._xml_root is None:
            if self.uri is None:
                raise Exception("Unable to fetch a new XML root for %s without a uri." % self)

            self.refresh()

        return self._xml_root

    @xml_root.setter
    def xml_root(self, root_node):
        """
        NOTE: setting xml_root directly will end-run around dirty object tracking.
        """
        self._xml_root = root_node

        if root_node is not None:
            # sets uri if available and needed
            self.uri = self.uri or root_node.get("uri")

            # name always overwrites.
            self._name = root_node.get("name")

    @lazy_property
    def limsid(self):
        """:type: str"""
        if self._limsid is None:
            if self.uri is not None and self.uri != "":
                self._limsid = self.uri.split('/')[-1]
            elif self.xml_root is not None:
                self._limsid = self._xml_root.get('limsid')
            else:
                raise Exception("No limsid available because there is no xml_root set")
        return self._limsid

    def post_and_parse(self, alternate_uri=None):
        """
        POST the current state of this object to a REST endpoint, then parse the response into this object.

        :param alternate_uri: Will be used instead of self.uri if provided.
        :type alternate_uri: str
        :raise requests.exceptions.HTTPError: If there are communication problems.
        :raise ClarityException: If Clarity returns an exception as XML.
        """
        target_uri = alternate_uri or self.uri
        if target_uri is None:
            raise Exception("Can't send element with no alternate_uri and no self.uri.")

        self.xml_root = self.lims.request('post', target_uri, self.xml_root)

    def put_and_parse(self, alternate_uri=None):
        """
        PUT the current state of this object to a REST endpoint, then parse the response into this object.

        :param alternate_uri: Will be used instead of self.uri if provided.
        :raise requests.exceptions.HTTPError: If there are communication problems.
        :raise ClarityException: If Clarity returns an exception as XML.
        """
        target_uri = alternate_uri or self.uri
        if target_uri is None:
            raise Exception("Can't send element with no alternate_uri and no self.uri.")

        self.xml_root = self.lims.request('put', target_uri, self.xml_root)

    def commit(self):
        """
        Shorthand for put_and_parse().
        """
        self.put_and_parse()

    def is_fully_retrieved(self):
        """
        :rtype: bool
        """
        return self._xml_root is not None

    def refresh(self):
        """
        Retrieve fresh element representation from the API.
        """
        self.xml_root = self.lims.request('get', self.uri)

    def invalidate(self):
        """
        Clear the local cache, forcing a reload next time the element is used.
        """
        self._xml_root = None

    def __repr__(self):
        return six.ensure_str(self.xml)
