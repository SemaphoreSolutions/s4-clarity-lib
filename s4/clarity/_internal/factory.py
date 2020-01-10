# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from typing import List, Iterable, Tuple, Optional, Type

from six.moves.urllib.parse import urlencode
from s4.clarity import ClarityException, ETree
import s4.clarity  # for typing
import re

from .element import ClarityElement, BatchFlags


class NoMatchingElement(ClarityException):
    pass


class MultipleMatchingElements(ClarityException):
    pass


class ElementFactory(object):
    """
    Provides access to a Clarity API endpoint. Implements conversion between XML and ClarityElement
    as well as caching and network services.

    :type lims: s4.clarity.LIMS
    :type element_class: classobj
    :type batch_flags: s4.clarity.BatchFlags
    """

    _params_re = re.compile(r'\?.*$')

    @staticmethod
    def _strip_params(string):
        return ElementFactory._params_re.sub('', string)

    def __init__(self,
                 lims,          # type: s4.clarity.LIMS
                 element_class  # type: Type[ClarityElement]
                 ):
        """
        Creates a new factory for `element_class`, intended to be used by/with the provided 
        `lims` instance to build Python objects to represent records in Clarity LIMS.
        
        If present, the following class attributes on `element_class` will be used as 
        configuration for this factory instance:
        
        NAME_ATTRIBUTE: (str) Name of the XML attribute in records of this object that
                        contains the name of the object. Defaults to "name".

        REQUEST_PATH: (str) Path (appended to the root URI of the `lims` instance) where
                      queries for objects of the given type should be sent.
                      Defaults to the plural of the element name, e.g. "artifacts" 
                      for Artifact.
        
        BATCH_FLAGS: (s4.clarity.BatchFlags) Determines which batch services the `lims` 
                     provides for the given element class. Defaults to `BatchFlags.NONE`.
        """

        self.lims = lims
        self.element_class = element_class
        self.name_attribute = getattr(self.element_class, 'NAME_ATTRIBUTE', "name")
        self.batch_flags = getattr(self.element_class, 'BATCH_FLAGS', BatchFlags.NONE)
        self._plural_name = self.element_class.__name__.lower() + "s"
        self.uri = self.lims.root_uri + getattr(self.element_class, 'REQUEST_PATH', "/" + self._plural_name)

        self._cache = dict()

        lims.factories[element_class] = self

    def new(self, **kwargs):
        # type: (**str) -> ClarityElement
        """
        Create a new ClarityElement pre-populated with the provided values.
        This object has yet to be persisted to Clarity.

        :param kwargs: Key/Value list of attribute name/value pairs to initialize the element with.
        :return: A new ClarityElement, pre-populated with provided values.
        """

        # creating some types requires using special tag, ie samples
        # are created by posting a 'samplecreation' element, not a 'sample'
        el_tag = getattr(self.element_class, 'CREATION_TAG', self.element_class.UNIVERSAL_TAG)

        # create xml_root, call class constructor
        new_xml_root = ETree.Element(el_tag)
        new_obj = self.element_class(self.lims, xml_root=new_xml_root)

        # set attributes from kwargs to new_object
        for k, v in kwargs.items():
            setattr(new_obj, k, v)

        return new_obj

    def add(self, element):
        # type: (ClarityElement) -> ClarityElement
        """
        Add an element to the Factory's internal cache and persist it back to Clarity.

        :type element: ClarityElement
        :rtype: ClarityElement
        """

        element.post_and_parse(self.uri)
        self._cache[element.uri] = element
        return element

    def delete(self, element):
        # type: (ClarityElement) -> None
        """
        Delete an element from the Factory's internal cache and delete it from Clarity.

        :type element: ClarityElement
        """

        self.lims.request('delete', element.uri)
        del self._cache[element.uri]

    def can_batch_get(self):
        # type: () -> bool
        """
        Indicates if Clarity will allow batch get requests.
        """
        return bool(self.batch_flags & BatchFlags.BATCH_GET)

    def can_batch_update(self):
        # type: () -> bool
        """
        Indicates if Clarity will allow batch updates.
        """
        return bool(self.batch_flags & BatchFlags.BATCH_UPDATE)

    def can_batch_create(self):
        # type: () -> bool
        """
        Indicates if Clarity will allow batch record creation.
        """
        return bool(self.batch_flags & BatchFlags.BATCH_CREATE)

    def can_query(self):
        # type: () -> bool
        """
        Indicates if Clarity will allow the user to submit queries.
        """
        return bool(self.batch_flags & BatchFlags.QUERY)

    def from_link_node(self, xml_node):
        # type: (ETree.Element) -> Optional[ClarityElement]
        """
        Will return the ClarityElement described by the link node.

        Link nodes are any xml element with the following attributes
        <element uri='...' name='...' limsid='...' />
        """

        if xml_node is None:
            return None
        obj = self.get(xml_node.get("uri"), name=xml_node.get("name"), limsid=xml_node.get("limsid"))
        return obj

    def from_link_nodes(self, xml_nodes):
        # type: (List[ETree.Element]) -> List[ClarityElement]
        """
        Will return the ClarityElements described by the link nodes.

        Link nodes are any xml element with the following attributes
        <element uri='...' name='...' limsid='...' />
        """

        objs = []
        for xml_node in xml_nodes:
            obj = self.from_link_node(xml_node)
            if obj is not None:
                objs.append(obj)
        return objs

    def from_limsid(self, limsid, force_full_get=False):
        # type: (str, bool) -> ClarityElement
        """
        Returns the ClarityElement with the specified limsid.
        """

        uri = self.uri + "/" + limsid
        return self.get(uri, limsid=limsid, force_full_get=force_full_get)

    def get_by_name(self, name):
        # type: (str) -> ClarityElement
        """
        Queries for a ClarityElement that is described by the unique name.
        An exception is raised if there is no match or more than one match.

        :raises NoMatchingElement: if no match
        :raises MultipleMatchingElements: if multiple matches
        """
        matches = self.query(**{self.name_attribute: name})
        if len(matches) == 0:
            raise NoMatchingElement("No %s found with name '%s'" % (self.element_class.__name__, name))
        elif len(matches) > 1:
            raise MultipleMatchingElements("More than one %s found with name '%s'" % (self.element_class.__name__, name))

        return matches[0]

    def get(self, uri, force_full_get=False, name=None, limsid=None):
        # type: (str, bool, str, str) -> ClarityElement
        """
        Returns the cached ClarityElement described by the provide uri. If the
        element does not exist a new cache entry will be created with the provided
        name and limsid.
        If force_full_get is true, and the object is not fully retrieved it will be refreshed.
        """

        uri = self._strip_params(uri)

        if uri in self._cache:
            obj = self._cache[uri]
        else:
            obj = self.element_class(self.lims, uri=uri, name=name, limsid=limsid)
            self._cache[uri] = obj

        if force_full_get and not obj.is_fully_retrieved():
            obj.refresh()

        return obj

    def post(self, element):
        # type: (ClarityElement) -> None
        """
        Posts the current state of the ClarityElement back to Clarity.
        """

        element.post_and_parse(self.uri)

    def batch_fetch(self, elements):
        # type: (Iterable[ClarityElement]) -> List[ClarityElement]
        """
        Updates the content of all ClarityElements with the current state from Clarity.
        Syntactic sugar for batch_get([e.uri for e in elements])

        :return: A list of the elements returned by the query.
        """

        return self.batch_get([e.uri for e in elements])

    def batch_get_from_limsids(self, limsids):
        # type: (Iterable[str]) -> List[ClarityElement]
        """
        Return a list of ClarityElements for a given list of limsids

        :param limsids: A list of Clarity limsids
        :return: A list of the elements returned by the query.
        """

        return self.batch_get([self.uri + "/" + limsid for limsid in limsids])

    def batch_get(self, uris, prefetch=True):
        # type: (Iterable[str], bool) -> List[ClarityElement]
        """
        Queries Clarity for a list of uris described by their REST API endpoint.
        If this query can be made as a single request it will be done that way.

        :param uris: A List of uris
        :param prefetch: Force load full content for each element.
        :return: A list of the elements returned by the query.
        """

        if not uris:
            return []  # just return an empty list if there were no uris

        if self.can_batch_get():
            links_root = ETree.Element("{http://genologics.com/ri}links")

            n_queries = 0

            querying_now = set()

            for uri in uris:
                uri = self._strip_params(uri)

                if uri in querying_now:
                    # already covered
                    continue

                obj = self._cache.get(uri)
                if prefetch and (obj is None or not obj.is_fully_retrieved()):
                    link = ETree.SubElement(links_root, "link")
                    link.set("uri", uri)
                    link.set("rel", self._plural_name)
                    querying_now.add(uri)
                    n_queries += 1

            if n_queries > 0:
                result_root = self.lims.request('post', self.uri + "/batch/retrieve", links_root)
                result_nodes = result_root.findall('./' + self.element_class.UNIVERSAL_TAG)

                for node in result_nodes:
                    uri = node.get("uri")
                    uri = self._strip_params(uri)

                    old_obj = self._cache.get(uri)
                    if old_obj is not None:
                        old_obj.xml_root = node
                    else:
                        new_obj = self.element_class(self.lims, uri=uri, xml_root=node)
                        self._cache[uri] = new_obj

            return [self._cache[uri] for uri in uris]

        else:
            return [self.get(uri, force_full_get=prefetch) for uri in uris]

    def _query_uri_and_tag(self):
        # type: () -> Tuple[str, str]
        """
        Return the uri and tag to use for queries. This can be overridden by subclasses when the
        the query uri doesn't follow the usual rule. Currently this is used to support queries for steps
        which are mapped to queries against processes and then mapped back to steps.
        Parse uri and tag from UNIVERSAL_TAG

        :return: Factory endpoint URI and tag. ex: ('http://genologics.com/ri/step', 'step')
        """
        return self.uri, self.element_class.UNIVERSAL_TAG.split('}', 2)[1]

    def all(self, prefetch=True):
        # type: (bool) -> List[ClarityElement]
        """
        Queries Clarity for all ClarityElements associated with the Factory.

        :param prefetch: Force load full content for each element.
        :return: List of ClarityElements returned by Clarity.
        """
        return self.query(prefetch)

    def query(self, prefetch=True, **params):
        # type: (bool, **str) -> List[ClarityElement]
        """
        Queries Clarity for ClarityElements associated with the Factory.
        The query will be made with the provided parameters encoded in the url.
        For the specific parameters to pass and the expected values please see the
        Clarity REST API.

        Some of the expected parameters contain the '-' character, in which
        case the dictionary syntax of this call will need to be used.

        Inline parameter names::

            query(singlevaluename='single value', multivaluename=['A', 'B', 'C'])

        Dictionary of parameters::

            query(prefetch=True, ** {
                'single-value-name': 'single value',
                'multi-value-name': ['A', 'B', 'C']
            })

        :param params: Query parameters to pass to clarity.
        :param prefetch: Force load full content for each element.
        :return: A list of the elements returned by the query.
        """
        if not self.can_query():
            raise Exception("Can't query for %s" % self.element_class.__name__)

        uri, tag = self._query_uri_and_tag()

        query_uri = uri + "?" + urlencode(params, doseq=True)

        elements = []

        while query_uri:
            links_root = self.lims.request('get', query_uri)

            link_nodes = links_root.findall('./' + tag)
            elements += self.from_link_nodes(link_nodes)
            next_page_node = links_root.findall('./next-page')
            if next_page_node:
                query_uri = next_page_node[0].get('uri')
            else:
                query_uri = None

        if prefetch:
            self.batch_fetch(elements)

        return elements

    def query_uris(self, **params):
        # type: (**str) -> List[str]
        """
        For backwards compatibility, use query() instead.
        Does a query and returns the URIs of the results.

        :param params: Query parameters to pass to clarity.
        """
        return [e.uri for e in self.query(False, **params)]

    def batch_update(self, elements):
        # type: (Iterable[ClarityElement]) -> None
        """
        Persists the ClarityElements back to Clarity. Will preform
        this action as a single query if possible.

        :param elements: All ClarityElements to save the state of.
        :raises ClarityException: if Clarity returns an exception as XML
        """

        if not elements:
            return

        if self.can_batch_update():
            details_root = ETree.Element(self.batch_tag)

            for el in elements:
                details_root.append(el.xml_root)

            self.lims.request('post', self.uri + "/batch/update", details_root)

        else:
            for el in elements:
                self.lims.request('post', el.uri, el.xml_root)

    def batch_create(self, elements):
        # type: (Iterable[ClarityElement]) -> List[ClarityElement]
        """
        Creates new records in Clarity for each element and returns these new records as ClarityElements.
        If this operation can be performed in a single network operation it will be.

        :param elements: A list of new ClarityElements that have not been persisted to Clarity yet.
        :return: New ClarityElement records from Clarity, created with the data supplied to the method.
        :raises ClarityException: if Clarity returns an exception as XML
        """

        if not elements:
            return []

        if self.can_batch_create():
            details_root = ETree.Element(self.batch_tag)

            for el in elements:
                details_root.append(el.xml_root)

            links = self.lims.request('post', self.uri + "/batch/create", details_root)

            return self.from_link_nodes(links)

        else:
            objects = []

            for el in elements:
                new_obj = self.element_class(
                    self.lims,
                    xml_root=self.lims.request('post', el.uri, el.xml_root)
                )
                self._cache[new_obj.uri] = new_obj
                objects.append(new_obj)

            return objects

    def batch_refresh(self, elements):
        # type: (Iterable[ClarityElement]) -> None
        """
        Loads the current state of the elements from Clarity. Any changes made
        to these artifacts that has not been pushed to Clarity will be lost.
        :param elements: All ClarityElements to update from Clarity.
        """

        # Clear the existing configs on samples this will force a refresh when queried
        # even though the samples are currently in the cache
        self.batch_invalidate(elements)

        # Now force load a new copy of the artifact state
        self.batch_fetch(elements)

    def batch_invalidate(self, elements):
        # type: (Iterable[ClarityElement]) -> None
        """
        Clears the current local state for all elements.
        :param elements: The ClarityElements that are to have their current state cleared.
        """

        for element in elements:
            element.invalidate()

    @property
    def batch_tag(self):
        return re.sub("}.*$", "}details", self.element_class.UNIVERSAL_TAG)
