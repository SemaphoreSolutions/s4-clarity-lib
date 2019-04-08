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
        self.step.details.commit()


if __name__ == "__main__":
    Normalization.main()
