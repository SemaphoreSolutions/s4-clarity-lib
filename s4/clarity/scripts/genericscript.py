# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc
import argparse
import copy
import inspect
import logging
import sys
import time

from .epp_output_formatter import EppOutputFormatter
from .htmllogging import HtmlLogFileHandler

# suppress warnings about Python Egg Cache being writable on Windows
if sys.platform.startswith('win'):
    import warnings
    warnings.filterwarnings("ignore", message=".+Python-Eggs is writable.+", category=UserWarning)

log = logging.getLogger(__name__)

# This value is returned to the operating system in the case of an error
SCRIPT_ERROR_RETURN_VALUE = 1

# This value is returned to the operating system when the script completed successfully
SCRIPT_SUCCESS_RETURN_VALUE = 0


class GenericScript(object):
    """
    GenericScript is the base abstract class for all of our script classes. The class
    provides common logging, argument parsing and entry point for all other script
    types.

    The GenericScript provides the main() method as an entry point for all scripts.
    Because your implementing class will be the main entry point for the program
    it will need to call the main method.

    The following code will make sure that the script is only run _if_ the file is the main
    python entry point:

        if __name__ == '__main__':
            YourSubClass.main()

    For more information on this see:

        https://docs.python.org/3/library/__main__.html
        https://stackoverflow.com/questions/419163/what-does-if-name-main-do

    Command line arguments can be added by overriding the add_arguments method. Remember to
    call the parent implementation of add_arguments so that all arguments are included.

    Example method adding an extra command line argument::

        @classmethod
        def add_arguments(cls, argparser):
            super(YourSubClass, cls).add_arguments(argparser)
            argparser.add_argument(
                '-t', '--thisparam', type=str, help='Something helpful', required=True
            )

    The values will be available in the self.options object.

    An example of printing the value passed in as --thisparam
    print self.options.thisparam

    This class works with the python logging system to gather log information
    and save it to a file. The files can be stored as html or plain text.

    To use this logging system in your own files declare the logging object
    at the top of each file:

        log = logging.getLogger(__name__)

    The log object can then be used to log information that the GenericScript will save.

    log.info("Low priority info to log.")
    log.warning("Warnings to log")
    log.error("Error conditions logged")

    To add functionality to a class derived from GenericScript the run() method must
    be overrode in the child class.
    """

    __metaclass__ = abc.ABCMeta

    # must be unicode, or python logging will die on non-ascii characters
    TEXT_LOG_FORMAT = u"%(asctime)s\t%(levelname)s\t%(name)s: %(message)s"
    final_summary = ""

    def __init__(self, options):
        """
        Creates a new instance of this class and saves the command line options

        :param options: The parsed command line options
        :type options: argparse.Namespace
        """
        self.options = options

    def open_log_output_stream(self):
        """
        override this for more complicated logging output.

        :rtype: io.IOBase
        """
        return self.options.logfile

    @classmethod
    def add_arguments(cls, parser):
        """
        Configures the Argument Parser to read command line input
        and store it in the self.options object.

        This method can be overrode in sub classes to provide extra arguments
        specific to the script being written. When this is done it is important to
        call the parent class add_arguemnts methods so that all arguments are included.

        :argument parser: The ArgumentParser that will be used to process the command line.
        :type parser: argparse.ArgumentParser
        """

        parser.add_argument(
            '-n', '--dry-run', action='store_true'
        )

        parser.add_argument(
            '-l', '--logfile', type=argparse.FileType('a'), default=None, nargs='?'
        )

        parser.add_argument(
            '--log-type', type=str, required=False, default='text', choices=['html', 'text']
        )

        def logleveltype(string):
            try:
                return logging.getLevelName(string.upper())
            except KeyError:
                # Log levels are in different properties in Python 2 and 3 modules
                try:
                    # Python 3
                    level_name_dict = logging._nameToLevel
                except:
                    # Python 2
                    level_name_dict = logging._levelNames
                msg = "%r is not a valid log level: use one of %s" % (
                    string,
                    list(filter(lambda k: type(k) == str, list(level_name_dict)))
                )
                raise argparse.ArgumentTypeError(msg)

        parser.add_argument(
            '--log-level', type=logleveltype, default=logging.INFO,
            help='Logging threshold. Default INFO.'
        )
        # separate level for console log stream for easier debugging
        parser.add_argument(
            '--log-level-console', type=logleveltype, default=logging.ERROR,
            help='Logging threshold for the console. Default ERROR.'
        )

    @abc.abstractmethod
    def run(self, *args):
        """
        The run method is called once the arguments are parsed and the logging is started.
        It will return an exit code indicating the success or failure of the process to run.
        Exit Codes: http://www.tldp.org/LDP/abs/html/exitcodes.html

        :return: The Exit code
        """
        return SCRIPT_SUCCESS_RETURN_VALUE

    @classmethod
    def _find_desc_and_epilog(cls):
        try:
            doclines = inspect.getmodule(cls).__doc__.splitlines()
        except AttributeError:
            doclines = []

        desc = None
        epilog = ""

        for l in doclines:
            l = l.strip()
            if l == "":
                continue
            if not desc:
                desc = l
                continue
            epilog += l + "\n"

        return desc, epilog

    def _start_logging(self):
        obfuscated_options = copy.copy(self.options)
        for attrname in obfuscated_options.__dict__.keys():
            if "password" in attrname:
                setattr(obfuscated_options, attrname, "******")

        # clear basic config handlers
        for h in logging.root.handlers:
            logging.root.removeHandler(h)
        logging.root.setLevel(logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.name = "Default console handler"
        console_handler.setLevel(self.options.log_level_console)
        console_handler.setFormatter(EppOutputFormatter(fmt=self.TEXT_LOG_FORMAT))
        logging.root.addHandler(console_handler)

        outstream = self.open_log_output_stream()

        if outstream is not None:
            obfuscated_options.logfile = outstream
            if self.options.log_type == 'html':
                file_handler = HtmlLogFileHandler(
                    outstream,
                    log_name=sys.argv[0]
                )
                file_handler.name = "HTML log handler"

            else:
                file_handler = logging.StreamHandler(outstream)
                file_handler.setFormatter(logging.Formatter(fmt=self.TEXT_LOG_FORMAT))
                file_handler.name = "Text log handler"

            file_handler.setLevel(self.options.log_level)
            logging.root.addHandler(file_handler)
        else:
            # no outstream
            console_handler.setLevel(self.options.log_level)

        self.loggingpreamble(obfuscated_options)

    @staticmethod
    def loggingpreamble(obfuscated_options):
        log.debug(
            "Environment: \n" +
            '\n'.join("     %s: %s" % (k, v)
                      for k, v
                      in obfuscated_options.__dict__.items())
        )

    @classmethod
    def main(cls):
        """
        The entry point for all scripts. This method will exit() the program
        upon completion.
        """

        # Configure the logging system to print to standard error
        # in case of errors before the full logging system is configured.
        logging.basicConfig()

        desc, epilog = cls._find_desc_and_epilog()

        argparser = argparse.ArgumentParser(
            description=desc,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            conflict_handler='resolve'
        )
        cls.add_arguments(argparser)

        options = argparser.parse_args()

        try:
            # Create a new instance of the implementing sub class
            instance = cls(options)

            # Start the logging system for the script
            instance._start_logging()

            # Log the starting of the script and record the start time
            log.debug("Starting %s.%s" % (cls.__module__, cls.__name__))
            start_time = time.time()

            # Call the implementing class' run() method
            result = instance.run()

            # Record the end time and record end of script, with elapsed time
            end_time = time.time()
            log.info("Elapsed time %.2f seconds." % (end_time - start_time))

            if instance.final_summary:
                # Write summary message directly to stdout, as the AI node uses the last line to display to the user
                sys.stdout.write(instance.final_summary)

        except Exception as e:
            log.error(str(e), exc_info=True)

            # Is this Request library specific logging? Could this be done by
            # looking for the correct exception subclass?
            if hasattr(e, "request_body") and e.request_body is not None:
                log.error("Request was: " + e.request_body)

            # If there was an exception tell the operating system
            # that the script did not complete successfully
            result = SCRIPT_ERROR_RETURN_VALUE

        finally:
            logging.shutdown()

        # Exit the program returning the result code to the operating system
        exit(result)
