# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import os

from setuptools import setup, find_packages

setup_dir = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(setup_dir, 's4', 'clarity', 'version.py'), 'r') as f:
    exec(f.read(), version)


with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='s4-clarity',
    version=version['__version__'],
    author='Semaphore Solutions',
    url='https://github.com/SemaphoreSolutions/s4-clarity-lib',
    author_email='info@semaphoresolutions.ca',
    description='A general purpose library for interacting with Clarity LIMS',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    python_requires='>=2.7',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    install_requires=(
        'requests',
        'argparse',
        'python-dateutil',
        'six',
        'future',
        'typing'
    ),
    tests_require=(
        'mock',
        'pytest'
    )
)
