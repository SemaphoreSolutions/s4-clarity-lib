# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc

from .shell import ShellScript


# abstract
class WorkflowTest(ShellScript):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def add_arguments(cls, argparser):
        super(WorkflowTest, cls).add_arguments(argparser)
        argparser.add_argument(
            '-s', '--skip', help="How many steps to skip.", type=int, default=0
        )
