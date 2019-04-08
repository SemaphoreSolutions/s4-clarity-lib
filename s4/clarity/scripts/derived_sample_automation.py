# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc
import s4.clarity

from .genericscript import GenericScript


class DerivedSampleAutomation(GenericScript):
    """
    A script run from the Project Dashboard screen.

    :ivar LIMS lims: The Clarity object to perform operations against.
    :ivar list[Artifact] artifacts: The list of Artifacts that the script applies to, loaded from the provided LIMS Ids.
    :param map options: A map of the values of the supplied command line arguments. The default keys available are:
        `username`, `password`, `api_uri`, and `derived_sample_ids`.

    *Usage:*

    Implement process_derived_samples(), which must return a string to display success status to the user.

    Optionally:
        add_arguments(argparser)  # To add more arguments. Don't forget to call super.

    Add to the end of your file:

    if __name__ == '__main__':
        YourSubClass.main()

    Example Clarity automation string. Contains an example of additional user input that would require an override of
    add_arguments to add the -x arg. *Note* that all userinput args are strings:

        ``python <script_name>.py -u {username} -p {password} -a '{baseURI}v2' -d {derivedSampleLuids} -x {userinput:input_x}``

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, options):
        super(DerivedSampleAutomation, self).__init__(options)
        self.lims = s4.clarity.LIMS(options.api_uri, options.username, options.password, options.dry_run)
        self.artifacts = self.lims.artifacts.batch_get_from_limsids(options.derived_sample_ids)

    @classmethod
    def add_arguments(cls, argparser):
        super(DerivedSampleAutomation, cls).add_arguments(argparser)
        argparser.add_argument(
            '-u', '--username', type=str, help='Clarity LIMS username', required=True
        )
        argparser.add_argument(
            '-p', '--password', type=str, help='Clarity LIMS password', required=True
        )
        argparser.add_argument(
            '-a', '--api-uri', type=str, help='URI of Clarity LIMS (ending in /api/v2)', required=True
        )
        argparser.add_argument(
            '-d', '--derived-sample-ids', type=str, nargs='+', help='LIMS IDs of derived samples (artifacts)'
        )

    def run(self):
        success_message = self.process_derived_samples()

        if not success_message:
            raise Exception("The process_derived_samples method must return a string message to use to report success.")

        self.final_summary = success_message

    @abc.abstractmethod
    def process_derived_samples(self):
        """
        Implement this to perform the work required. Method *must* return a summary success string, as it's used to
        display the user-facing message on script completion.

        :return: Message to report success to the user
        :rtype: str
        :raise: Exception to report failure
        """
        raise NotImplementedError("Call to abstract method '%s'." % repr(classmethod))
