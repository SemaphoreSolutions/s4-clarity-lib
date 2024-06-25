# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import sys
import abc
import argparse
import re

import s4.clarity

from s4.clarity.scripts import GenericScript


class StepEPP(GenericScript):
    """
    This class forms the base of the scripting for Step EPP scripts run from Clarity.
    It will provide access to a LIMS object as well as the Step data for the
    currently running step.

    If the log file name that gets passed in over the command line is the limsId clarity
    assigned to an file it will be automatically uploaded at the end of the step.

    :vartype step: s4.clarity.step.Step
    :ivar step: The Clarity Step to execute the script against.
    :vartype lims: LIMS
    :ivar lims: The Clarity LIMS object to use for API operations.
    """
    __metaclass__ = abc.ABCMeta

    PREFETCH_INPUTS = 'inputs'
    PREFETCH_OUTPUTS = 'outputs'
    PREFETCH_SAMPLES = 'samples'

    def __init__(self, options):
        """
        Creates a new StepEPP object and initializes the local LIMS and Step objects.

        :param options: Parsed command line options
        """

        super(StepEPP, self).__init__(options)
        self.lims = s4.clarity.LIMS(options.lims_root_uri, options.username, options.password, options.dry_run, options.insecure)
        self.step = self.lims.step_from_uri(options.step_uri)

    @staticmethod
    def display(*args):
        sys.stderr.write(*args)
        sys.stderr.write("\n")
        sys.stderr.flush()

    def open_log_output_stream(self):
        """
        Use step's logfile.
        """
        if self.options.logfile:

            # Log files that are shared by Python and LLTK/LITKs on a step must
            # use the same file name in order to prevent bugs. In Clarity 5 and
            # earlier, the file name used by LLTK/LITKs is simply the limsid of
            # the ResultFile. But in Clarity 6 and later it has "LogFile"
            # appended to the name, and so we need to check the active Clarity
            # version and adjust our behaviour accordingly.

            filename = self.options.logfile
            revision = int(self.lims.current_minor_version[1:])
            if revision >= 31:  # Clarity 6.0 has an API minor version of 31
                filename = "%s-LogFile" % filename

            if self.options.log_type == 'html':
                filename = "%s.html" % filename
                content_type = 'text/html'
            elif self.options.log_type == 'text':
                filename = "%s.log" % filename
                content_type = 'text/plain'
            else:
                raise Exception("Unrecognized log type %s", self.options.log_type)

            try:
                f = self.step.open_resultfile(filename, "a", only_write_locally=True, limsid=self.options.logfile)
                f.content_type = content_type
                return f
            except s4.clarity.ClarityException as ex:
                # raise a new exception with a clearer message, preserving traceback
                raise s4.clarity.ClarityException(
                    "While trying to open log file %s: " % self.options.logfile + str(ex))
        else:
            return super(StepEPP, self).open_log_output_stream()

    @classmethod
    def add_arguments(cls, argparser):
        super(StepEPP, cls).add_arguments(argparser)
        argparser.add_argument(
            '-u', '--username', type=str, help='Clarity LIMS username', required=True
        )
        argparser.add_argument(
            '-p', '--password', type=str, help='Clarity LIMS password', required=True
        )
        argparser.add_argument(
            '-i', '--step-uri', type=str, help='URI of Clarity LIMS step', required=True,
            action=_StoreAndExtractRootUriAction
        )
        argparser.add_argument(
            '-l', '--logfile', type=str, help='LIMS ID of logfile artifact', required=False
        )
        argparser.add_argument(
            '--insecure', action='store_true', help='Disables SSL Certificate validation.', required=False,
        )
        argparser.set_defaults(log_type='html')

    # -----------------------------------------------------------------
    # convenience methods
    # -----------------------------------------------------------------

    def prefetch(self, *categories):
        """
        Fetch values for input artifacts, output artifacts, or samples in a batch.

        Input and output samples are always an identical set, so 'samples' will fetch both.

        Note: when only samples are selected, input artifacts will also be fetched. To change this behaviour,
        supply both 'outputs' and 'samples' in the categories list.

        :param categories: List of any number of the strings: 'inputs', 'outputs', 'samples'.
        :type categories: str|list[str]

        :returns: a list of all fetched objects
        :rtype: list[ClarityElement]
        """

        for item in categories:
            if item not in (StepEPP.PREFETCH_OUTPUTS, StepEPP.PREFETCH_INPUTS, StepEPP.PREFETCH_SAMPLES):
                raise ValueError("Unrecognized item '%s' in %s.prefetch" % (item, self.__class__))

        if len(categories) == 1 and categories[0] == StepEPP.PREFETCH_SAMPLES:
            # only samples are requested and not artifacts, but we need artifacts to get samples.
            # ensure we always fetch artifacts; default to fetching inputs.
            categories = [StepEPP.PREFETCH_INPUTS, StepEPP.PREFETCH_SAMPLES]

        artifacts = []
        if StepEPP.PREFETCH_INPUTS in categories:
            artifacts += self.step.details.inputs
        if StepEPP.PREFETCH_OUTPUTS in categories:
            artifacts += self.step.details.outputs

        self.lims.artifacts.batch_fetch(artifacts)

        if StepEPP.PREFETCH_SAMPLES in categories:
            # use the artifacts that we prefetched to find samples.
            # we use a set because we may have both inputs and outputs in the artifacts_to_fetch list.
            samples = list({sample for a in artifacts for sample in a.samples})
            self.lims.samples.batch_fetch(samples)
            return samples + artifacts

        else:
            return artifacts

    @property
    def inputs(self):
        """
        Shortcut for self.step.details.inputs.

        :rtype: list[Artifact]
        """
        return self.step.details.inputs

    @property
    def outputs(self):
        """
        Shortcut for self.step.details.outputs.

        :rtype: list[Artifact]
        """
        return self.step.details.outputs

    @property
    def iomaps(self):
        """
        Shortcut for self.step.details.iomaps.

        :rtype: list[IOMap]
        """
        return self.step.details.iomaps


class _StoreAndExtractRootUriAction(argparse.Action):
    """
    Argparse Action to properly parse the Clarity URI
    """

    _LIMS_ROOT_URI_RE = re.compile(r'^https?://[^/]+/api/v2/')

    def __call__(self, parser, namespace, value, option_string=None):
        # first actually set namespace.<dest> = value
        setattr(namespace, self.dest, value)

        m = self._LIMS_ROOT_URI_RE.match(value)
        if not m:
            raise argparse.ArgumentError(self, "Invalid Clarity Step URI")

        # set lims_root_uri to extracted root
        setattr(namespace, 'lims_root_uri', m.group(0))
