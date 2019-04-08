====================
Clarity-Integrations
====================

Semaphore libraries, packages, and scripts for Clarity.


Package Setup
-------------
In the root directory of the client project where the S4 library is to be used, create a file called ``project.py``.
This Python file should call into the S4 library's ``makepackage`` method with the following parameters:

- name (string): optional, defaults to directory name.
- source_directory (string): where the project source code is located
- include_libraries (list[string]): list of project library directories to include
- prod_requires (list[string]): list of external Python modules that are required
- excludes (list[string]): optional, patterns to exclude in the package directory
- format (string): the type of archive to use. Options are ``zip``, ``gztar``, ``bztar``, and ``tar``
- version (string): used for package naming. Can replace the --version option provided on the command line.

An example package.py file::

    from s4.packager import makepackage

    makepackage(
        name='Sample Project',
        source_directory='custom_extensions',
        include_libraries=[
            's4.clarity',
            's4.utils',
            's4.scripting',
            's4.steputils',
            'webservice'
        ],
        prod_requires=[
            'requests',
            'argparse',
            'python-dateutil',
            'lxml',
            'flask',
            'flask_httpauth'
        ],
        excludes=[
            'webservice/tests',
            'webservice/ui'
        ],
        format='gztar',
        version='1.0'
    )

Making a package
----------------
Dev or Test builds:

- From the client project root, run ``./package.py --no-git --version <dev-name>`` to build a local package without creating a new Git tag.

Release build:

- From the client project root, run ``./package.py --version <release-name>``, which will build a local package, and also create a Git tag matching the value of the ``version`` property.

Packages will be created into the /dist directory of the client project.

Deploying
---------
Follow the client-specific deploy instructions appropriate for your project.

In general, the minimal basic steps are:

- Copy the package to the target server and unpack it to the desired location.
- Install Python dependencies using pip, pointing at the project's requirements.txt file.

Documentation
-------------
To build the documentation, run ``make html`` from the docs directory.