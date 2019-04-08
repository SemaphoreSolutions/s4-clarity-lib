# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property


class Permission(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/permission}permission"

    description = subnode_property("description")
    action = subnode_property("action")
