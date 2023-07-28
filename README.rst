
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


.. code-block:: python

    from s4.clarity.scripts import TriggeredStepEPP

    LibraryVolume = 2.0
    MolWeightBasePair = 660 * 1e6  # micrograms / mol
    AssumedBasePairs = 400.0
    TargetMolarity = 4.0
    Overage = 4


    class Normalization (TriggeredStepEPP):
        def on_record_details_enter(self):
            self.prefetch(self.PREFETCH_INPUTS, self.PREFETCH_OUTPUTS)

            for iomap in self.step.details.iomaps:
                library_concentration = iomap.input["Concentration"]
                library_molarity = library_concentration / (AssumedBasePairs * MolWeightBasePair)
                iomap.output["Concentration"] = library_concentration
                iomap.output["Molarity (nM)"] = library_molarity
                iomap.output["Library Vol (uL)"] = LibraryVolume
                iomap.output["Tris HCl (uL)"] = LibraryVolume * (library_molarity / TargetMolarity - 1)

            self.lims.artifacts.batch_update(self.step.details.outputs)


    if __name__ == "__main__":
        Normalization.main()

Installation
------------

To install s4-clarity, simply use pip::

    $ pip install s4-clarity

