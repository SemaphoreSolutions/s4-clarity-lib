# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import six
import logging
import time
from xml.sax.saxutils import escape
from textwrap import dedent


class HtmlFormatter(logging.Formatter):

    # must be uncode, or python logging dies on non-ascii messages
    basic_format = u"[%(asctime)s] [%(levelname)s] - %(message)s"
    multiline_format = u"[%(asctime)s] [%(levelname)s] - <p style='margin-left:4em'>%(message)s</p>"

    time_format = "%Y/%m/%d %H:%M:%S"

    def formatTime(self, record, datefmt=None):
        return logging.Formatter.formatTime(self, record, self.time_format)

    def format(self, record):
        """
        :type record: logging.LogRecord
        """

        if record.args:
            # don't let logging.Formatter do this, because then we can't call cgi.escape on the result.
            record.msg = record.msg % record.args
            record.args = None

        self._fmt = self.basic_format

        if record.msg:
            record.msg = escape(six.u(record.msg))

            if '\n' in record.msg:
                self._fmt = self.multiline_format

        return logging.Formatter.format(self, record)

    def formatException(self, ei):
        basic_lines = logging.Formatter.formatException(self, ei)
        return """<pre style='background-color: #28DD31;
                white-space: pre-wrap; /* css-3 */
                white-space: -moz-pre-wrap !important; /* Mozilla, since 1999 */
                white-space: -pre-wrap; /* Opera 4-6 */
                white-space: -o-pre-wrap; /* Opera 7 */
                word-wrap: break-word; /* Internet Explorer 5.5+ */
                border: 1px double #cccccc;
                padding: 5px;'>""" + \
               basic_lines + "</pre>"


class HtmlLogFileHandler(logging.StreamHandler):
    prologue = dedent("""
    <html>
      <body>
        <h1 style='margin:0.25em;font-size:12pt;font-family:serif'>[%(date)s] External script %(name)s started:</h1>
        <pre style='white-space: pre-wrap; /* css-3 */
                white-space: -moz-pre-wrap !important; /* Mozilla, since 1999 */
                white-space: -pre-wrap; /* Opera 4-6 */
                white-space: -o-pre-wrap; /* Opera 7 */
                word-wrap: break-word; /* Internet Explorer 5.5+ */
                border: 1px double #cccccc;
                padding: 5px;
                background-color: #28DD31'>""")

    epilogue = dedent("""</pre>
      </body>
    </html>
    """)

    def __init__(self, output_stream, log_name):
        """
        :type output_stream: io.IOBase
        :type log_name: str
        """

        self._stringdict = {
            'name': log_name,
            'date': time.strftime(HtmlFormatter.time_format)
        }

        output_stream.write(self.prologue % self._stringdict)

        logging.StreamHandler.__init__(self, output_stream)
        self.setFormatter(HtmlFormatter())

    def close(self):
        if self.stream:
            self.stream.write(self.epilogue % self._stringdict)
            self.flush()
            if hasattr(self.stream, "close"):
                self.stream.close()
            logging.StreamHandler.close(self)
            self.stream = None

    def emit(self, record):
        logging.StreamHandler.emit(self, record)
