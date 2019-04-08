from xml.sax.saxutils import escape
import logging

from .user_message_exception import UserMessageException


class EppOutputFormatter(logging.Formatter):
    """
    Clarity will display the console output of an EEP in an error message box
    if the script returns a non-zero result. This means that the console
    output may be displayed in a web page, and needs to have HTML encoding apply
    """

    def format(self, record):
        """
        :type record: logging.LogRecord
        """

        if record.exc_info is not None:
            etype, value, tb = record.exc_info
            if etype is UserMessageException:
                return escape(str(record.msg))

        if record.args:
            # don't let logging.Formatter do this, because then we can't call escape on the result.
            record.msg = record.msg % record.args
            record.args = None

        if record.msg:
            record.msg = escape(str(record.msg))

        return logging.Formatter.format(self, record)

    def formatException(self, ei):

        # Break up the tuple
        etype, value, tb = ei

        if etype is UserMessageException:
            # User message exceptions are to be displayed to the user
            # as is, do not include full exception info.
            return ""

        return escape(logging.Formatter.formatException(self, ei))

