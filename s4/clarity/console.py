# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import code

# this is unused, but it has the side effect of enabling GNU readline support in the console.
import readline

import s4.clarity.scripts.shell


class ClarityConsole(s4.clarity.scripts.shell.ShellScript):
    """
    How to use:

    python -m s4.clarity.console -r http://s4clarityconfig:ssh/api/v2 -u admin -p apassword

    In this python console you are "inside" the LIMS object. That means that your local namespace
    is equal to the set of functions and instance variables defined on the object.


    Examples

    To list all researchers with the username admin:
    >>> researchers.query(username='admin')

    To find all artifacts (this is dumb don't do this):
    >>> results = artifacts.all()

    Grab a specific artifact and set a UDF:
    >>> art = artifact('92-1376')
    >>> art["Tumor Area (mm^2)"] = 17
    >>> art.commit()

    Type 'funcs()' on the command line to see an automatically-generated list. This is also
    a standard Python console so you can import, etc, as normal.
    """

    def __init__(self, options):
        super(ClarityConsole, self).__init__(options)
        self.namespace_list = None
        self.console = None

    def print_namespace_list(self):
        if self.namespace_list is None:
            raise Exception("namespace_list is None, this shouldn't happen")
        if self.console is None:
            raise Exception("console is None, this shouldn't happen")

        self.console.write("Functions available by default in this namespace:\n" + self.namespace_list)

    def run(self):
        # do a test query to see if we're connected
        self.lims.labs.all(prefetch=False)

        namespace = {
            'lims': self.lims
        }

        for attr in dir(self.lims):
            if attr.startswith('_'):
                continue

            namespace[attr] = getattr(self.lims, attr)

        self.namespace_list = '\n'.join([("\t%s" % attr) for attr in namespace if not attr.startswith('_')])

        namespace['__name__'] = '__console__'
        namespace['funcs'] = self.print_namespace_list

        self.console = code.InteractiveConsole(namespace)

        banner = "Python s4-clarity console connected to %s as %s\n" \
                 "Type 'funcs()' for a list of available functions.\n" % \
                 (self.lims.hostname, self.lims.username)
        self.console.interact(banner)


if __name__ == "__main__":
    ClarityConsole.main()
