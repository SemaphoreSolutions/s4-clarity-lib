# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------


class UserMessageException(Exception):
    """
    Stops the currently running EPP and displays a message box to the user.
    The message box is like other exceptions but will not display a stack trace.
    """
    pass

