Release History
===============
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