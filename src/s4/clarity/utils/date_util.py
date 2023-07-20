# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import dateutil.parser


def str_to_date(string):
    """
    :type string: str
    :rtype: datetime.date
    """
    return dateutil.parser.parse(string,yearfirst=True).date()


def str_to_datetime(string):
    """
    :type string: str
    :rtype: datetime
    """
    return dateutil.parser.parse(string,yearfirst=True)


def date_to_str(dt):
    """
    :type dt: datetime.date
    :rtype: str
    """
    return dt.strftime("%Y-%m-%d")


def datetime_to_str(dt):
    """
    :type dt: datetime.datetime
    :rtype: str
    """
    return dt.strftime("%Y-%m-%dT%T%:z")
