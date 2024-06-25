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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    install_requires=(
        'requests',
        'argparse',
        'python-dateutil',
        'six',
        'future',
        "typing; python_version < '3.5'"
    ),
    tests_require=(
        'mock',
        'pytest'
    ),
    project_urls={
        'Documentation': 'https://readthedocs.org/projects/s4-clarity-lib',
        'Source': 'https://github.com/SemaphoreSolutions/s4-clarity-lib',
    }
)
