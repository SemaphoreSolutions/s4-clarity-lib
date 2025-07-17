Release History
===============
1.7.1
-
- (#78) Added functionality to remove individual reagent lots (`StepReagentLots.remove_reagent_lots()`), and clear all reagent lots (`StepReagentLots.clear_reagent_lots()`) from a step.

1.7.0
-
- (#71) Added support for instrument types:
   - Added a new `InstrumentType` class
   - Modified the `Instrument` class to return `InstrumentType` objects when reading the `instrument_type` property
   - Modified the `StepDetails` class to return `InstrumentType` objects when reading the `permitted_instrument_types` property
   - Added a new `instrument_types` property to the `LIMS` class that can query instrument types.
   - The `Instrument` class now correctly reports instrument limsids.
   - The `instrument_used` property of `StepDetails` is now writable.
- Several updates to `StepRunner`:
   - (#69) Step runners now support running the same step multiple times within a protocol.
   - (#76) Step runners can now sign steps that require an eSignature, by calling `self.sign()` from the `record_details()` method.
- (#68) The "Leave in QC Protocol" artifact action can now be selected at the Next Steps screen by using `step.actions.artifact_actions[artifact].leave_in_qc_protocol()`
- (#67) The `replace_and_commit_from_local` method of the `File` class now supports an optional `name` parameter, allowing you to upload a file to Clarity using a different name from the on-disk filename.
- (#65) Fixes a bug in `StepConfiguration.permitted_containers()` that caused steps with no permitted containers (i.e. no-output steps) to return all container types instead of none. 
- (#63) Added the `Step.clear_pools()` method which can be used to remove any existing pools that were created on a step.

1.6.1
-
- Explicitly declare requests >= 2.22.0 and urllib3 >= 1.25.2 as dependencies, which fixes an edge case causing the `lims.versions` and `lims.current_minor_version` properties to raise an exception on early versions of Python 3.6.

1.6.0
-
- (#60) Added support for Python 3.12.
- (#55) Step placements can now be updated without having to clear existing placements first.
- (#53) Fix an issue that prevented `StepRunner.add_default_reagents()` from working correctly on Clarity 6.1+ if the step being run contains an archived reagent kit.
- (#51) Fix an issue that could cause log messages to become duplicated, or disappear, when `s4-clarity-lib` is being used in tandem with an LLTK/LITK on the same step in Clarity 6.0+.
- (#51) Added `lims.versions` and `lims.current_minor_version` properties.

1.5.0
-
- (#45) Added the `permitted_containers` property to `StepConfiguration`.
- (#43) Added support for the Step Setup state to `StepRunner`.
- (#42) Improved Documentation, testing and function naming around container types and well ordering.

1.4.2
-
- Migrated CI/CD from Travis-CI to GitHub Actions.
- No code changes since 1.4.1, just pushing a release to verify that we can still deploy to PyPi!

1.4.1
-
- (#40) Fixed a typo that prevented the `supplier` property from being set on an instance of `ReagentKit`.

1.4.0
- 
- (#34) Now fully compatible with Python 3.10.
- (#35) The `insecure` and `dry-run` parameters may now be used together when creating a LIMS object.

1.3.1
-
- (#33) Fixed regression in 1.3.0 which caused all stage-based routing to fail

1.3.0
-
- (#25) Added support for the [Clarity Instruments API endpoint](https://d10e8rzir0haj8.cloudfront.net/5.3/rest.version.instruments.html):
   - Added a new `Instrument` class
   - Updated `StepConfiguration` (in `configuration.protcol`) and `StepDetails` (in `step`) to retrieve `instrument` related xml subnodes
- (#24) Add a `files` property to the `Project` class
- (#30) Fixed `workflow.enqueue()` setting `stage-uri` in generated XML if `stage` appears in the domain name
- (#28) Removed dependency on `typing` for Python versions 3.5 and up
- Updated documentation:
   - (#27) The `StepProgramStatus` class documentation now more accurately reflects usage
   - (#29) The documentation of the `Stage` class has corrected to show that the `step` property returns a `StepConfiguration` object

1.2.0
-
- Fix `ClarityElement.__repr__` to always return a string to avoid exceptions in Python 3.x  
- Fix incorrect universal tag for ControlType that prevented the creation of Control Types using the library
- Add is_published property to the File object

1.1.1
-
- Remove timeout from wait_for_epp

1.1.0
-
- Add suport for Clarity 5 demux endpoint
- Add support for timeouts on Clarity HTTP requests

1.0.0
-
- s4.scripting -> s4.clarity.scripts
- s4.steputils -> s4.clarity.steputils
- s4.utils -> s4.clarity.utils

- Removed s4.bartender
- Removed s4.packager
- Removed s4.clarity.monitor

0.3.0
-
Python 3 internal 