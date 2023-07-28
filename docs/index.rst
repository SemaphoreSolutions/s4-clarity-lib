.. s4-clarity documentation master file

==================
S4-Clarity Library
==================


.. image:: https://github.com/SemaphoreSolutions/s4-clarity-lib/actions/workflows/ci.yml/badge.svg?branch=master
    :target: https://github.com/SemaphoreSolutions/s4-clarity-lib/actions


Used in numerous labs around the world, the S4-Clarity library provides an easy-to-use integration with the BaseSpace Clarity LIMS API. The package includes:
   - Classes representing familiar Clarity API entities that provide read-write access to most properties.
   - Helper methods that simplify common operations.
   - Base classes for scripts that integrate with Clarity: EPPs, DSAs, and shell scripts.
   - Utilities that help with Clarity-related tasks, such as managing config slices, or automating the completion of a Step.

The S4-Clarity library lets developers interact with the Clarity API in fewer lines of code. With HTTP and XML boilerplate out of the way, you'll have your integration built in no time at all.


.. include:: examples/normalization.py
    :code: python


User Guide
----------

.. toctree::
    :maxdepth: 3

    guide/intro

API Details
-----------

.. toctree::
    :maxdepth: 2

    api/clarity
    api/scripts
    api/utils
    api/steputils
