

## Testing

### Basic

The tests use [pytest](https://readthedocs.org/projects/pytest/).

To run the test suite, run the following in a fresh virtualenv:

    pip install -r requirements.txt
    pytest

### Testing multiple Python versions with Tox

You will need to install [Tox](https://tox.readthedocs.io/en/latest/).
The test suite can then be run in multiple Python versions as follows:

    tox

By default, Tox looks for `tox.ini` in the current directory, and uses it to determine
which Python versions to use, which requirements to install, how to run the tests, etc.

### Testing using Travis CI

See `.travis.yml`.

Travis CI is set up on the official Github repo (https://github.com/SemaphoreSolutions/s4-clarity-lib).
It runs automatically on every pull request.
