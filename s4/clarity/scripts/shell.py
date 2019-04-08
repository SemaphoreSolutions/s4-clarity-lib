# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc
import s4.clarity

from s4.clarity.scripts import GenericScript


class ShellScript(GenericScript):
    """
    ShellScript provides the framework for a basic shell script that will communicate with Clarity.
    It provides all of the functionality of a GenericScript with the addition of a LIMS object.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, options):
        """
        Creates a new instance of this class and saves the command line options

        :param options: The parsed command line options
        :type options: argparse.Namespace
        """

        super(ShellScript, self).__init__(options)
        self.lims = s4.clarity.LIMS(options.lims_root_uri, options.username, options.password, options.dry_run, options.insecure)

    @classmethod
    def add_arguments(cls, parser):
        """
        Add command line arguments to be parsed.

        :argument parser: The ArgumentParser that will be used to process the command line.
        :type parser: argparse.ArgumentParser
        """
        super(ShellScript, cls).add_arguments(parser)

        parser.add_argument(
            '-u', '--username', type=str, help='Clarity LIMS username', required=True
        )

        parser.add_argument(
            '-p', '--password', type=str, help='Clarity LIMS password', required=True
        )

        parser.add_argument(
            '-r', '--lims-root-uri', type=str, help='URI of Clarity LIMS (ending in /api/v2/)', required=True
        )

        parser.add_argument(
            '--insecure', action='store_true', help='Disables SSL Certificate validation.', required=False,
        )
