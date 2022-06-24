Release History
===============
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