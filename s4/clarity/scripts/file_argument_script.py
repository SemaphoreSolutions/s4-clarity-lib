# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc
import json
import os
import s4
import logging
from io import open
from .genericscript import GenericScript


log = logging.getLogger(__name__)


class FileArgumentScript(GenericScript):
    """
    A GenericScript that will provide a LIMS object as well as
    populate the self.file_options object with the data from
    a file containing a single JSON object.

    This is used to pass complex arguments that would not be suitable
    to pass over the command line.
    """

    __metaclass__ = abc.ABCMeta

    @classmethod
    def add_arguments(cls, argparser):
        super(FileArgumentScript, cls).add_arguments(argparser)

        argparser.add_argument('--param_file', type=str, required=True)
        argparser.add_argument('-r', '--lims-root-uri', type=str, help='URI of Clarity LIMS (ending in /api/v2/)', required=True)
        argparser.add_argument('-u', '--username', type=str, help='Clarity LIMS username', required=True)
        argparser.add_argument('-p', '--password', type=str, help='Clarity LIMS password', required=True)
        argparser.add_argument('--insecure', action='store_true', help='Disables SSL Certificate validation.', required=False)

    def __init__(self, options):
        super(FileArgumentScript, self).__init__(options)

        self.lims = s4.clarity.LIMS(options.lims_root_uri, options.username, options.password, options.dry_run, options.insecure)

        # ToDo: It would be nice if this could just add extra values to self.options
        self.file_options = self.get_options_from_file(self.options.param_file)

    def _read_file_option(self, option_name, default_value=None):
        try:
            return self.file_options[option_name]
        except KeyError:
            if default_value is None:
                raise Exception("Unable to read value '%s' from JSON file." % option_name)
            return default_value

    @staticmethod
    def get_options_from_file(file_name):
        if not os.path.isfile(file_name):
            raise Exception("Argument file does not exist: %s" % file_name)

        options_file = open(file_name, mode="r", encoding="utf-8")
        return json.load(options_file)
