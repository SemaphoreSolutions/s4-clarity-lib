# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import os
import logging
from io import open
from s4.clarity import ClarityException
from s4.clarity.scripts.user_message_exception import UserMessageException

log = logging.getLogger(__name__)


def save_file_to_path(step, target_directory, limsid, file_name=None):
    """
    Saves step output files to the specified directory.

    :param step: The step which contains the files to save.
    :param target_directory: The directory path to save files to.
    :param limsid: The lims id of the file to save.
    :param file_name: Optional file name to use when saving the file to disk. It allows renaming on save.
    """

    try:
        step_file = step.open_resultfile(None, "rb", limsid=limsid)

        # If there is no uri then a file has not been saved to this id
        if step_file.uri is None:
            log.warning("LimsId %s has no file to save." % limsid)
            return

        if file_name is None:
            file_name = os.path.basename(step_file.name)

        file_path = os.path.join(target_directory, file_name)
        log.info("Saving %s to %s" % (limsid, file_path))

        with open(file_path, "wb") as output_file:
            step_file.pipe_to(output_file)

    except ClarityException:
        raise UserMessageException("Unable to save file to '%s'" % target_directory)

