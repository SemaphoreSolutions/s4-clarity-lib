# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import datetime

import s4.clarity.utils
import six

NUMERIC = "Numeric"
STRING = "String"
TEXT = "Text"
URI = "URI"
DATE = "Date"
DATETIME = "Datetime"
BOOLEAN = "Boolean"

ALL_TYPES = [NUMERIC, STRING, TEXT, URI, DATE, DATETIME, BOOLEAN]


def clarity_string_to_obj(typename, string):
    """
    Convert field value string to Python object.

    :type typename: str
    :type string: str
    :rtype: object
    """
    if string is None:
        return None
    if typename in [STRING, TEXT, URI]:
        return string
    elif typename == NUMERIC:
        return float(string)
    elif typename == DATE:
        return s4.clarity.utils.str_to_date(string)
    elif typename == DATETIME:
        return s4.clarity.utils.str_to_datetime(string)
    elif typename == BOOLEAN:
        return string == 'true'
    else:
        raise Exception("Unknown type '%s'" % typename)


def obj_to_clarity_string(obj):
    """
    Convert Python object to field value string.

    :rtype: str
    """
    if obj is None:
        return ""
    elif isinstance(obj, six.string_types):
        return obj
    elif isinstance(obj, bool):
        # Check bool before numerics, as bool is a subtype of int
        return "true" if obj else "false"
    elif isinstance(obj, (float, int)):
        return repr(obj)
    elif isinstance(obj, datetime.date):
        return s4.clarity.utils.date_to_str(obj)
    elif isinstance(obj, datetime.datetime):
        return s4.clarity.utils.datetime_to_str(obj)
    else:
        raise Exception("Unknown object type '%s'" % type(obj).__name__)


def clarity_typename_to_python_typename(clarity_typename):
    """
    Convert Clarity typename to the Python typename

    :type clarity_typename: str
    :rtype: str
    """
    if clarity_typename == NUMERIC:
        return "number"
    elif clarity_typename in [STRING, TEXT, URI]:
        return "str"
    elif clarity_typename == DATE:
        return "datetime.date"
    elif clarity_typename == DATETIME:
        return "datetime"
    elif clarity_typename == BOOLEAN:
        return "bool"
    else:
        raise Exception("Unknown clarity typename '%s'" % clarity_typename)
