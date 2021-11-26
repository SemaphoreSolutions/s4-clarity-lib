# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement, FieldsMixin
from s4.clarity._internal.props import subnode_property, subnode_link, subnode_links
from s4.clarity.researcher import Researcher
from s4.clarity.file import File
from s4.clarity import types


class Project(FieldsMixin, ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/5.3/rest.version.projects.html
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/project}project"
    ATTACH_TO_NAME = "Project"

    open_date = subnode_property("open-date", types.DATE)
    close_date = subnode_property("close-date", types.DATE)
    invoice_date = subnode_property("invoice-date", types.DATE)
    researcher = subnode_link(Researcher, "researcher", attributes=('uri',))  # type: Researcher
    files = subnode_links(File, File.UNIVERSAL_TAG)
