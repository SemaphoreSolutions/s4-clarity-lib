# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging

# import whichever xml etree is available and re-export it for the rest of the library
try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

from ._internal.lazy_property import lazy_property
import s4.clarity.utils.ssh

from .exception import ClarityException
from .lims import LIMS
from ._internal import ClarityElement
from ._internal.factory import ElementFactory
from ._internal.stepfactory import StepFactory
from ._internal.udffactory import UdfFactory
try:
    # Python <2.7.9 has insecure OpenSSL, but that doesn't mean we want to hear about it on every line.
    # Sometimes this works, sometimes disable_warnings doesn't exist.
    try:
        import urllib3
    except ImportError:
        import requests.packages.urllib3 as urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
except:
    pass

log = logging.getLogger(__name__)

module_members = [
    ClarityElement,
    ClarityException,
    ElementFactory,
    lazy_property,
    LIMS,
    StepFactory,
    UdfFactory
]

__all__ = [m.__name__ for m in module_members]

# The below __module__ assignments allow Sphinx to generate links that point to this parent module.
for member in module_members:
    member.__module__ = "s4.clarity"
