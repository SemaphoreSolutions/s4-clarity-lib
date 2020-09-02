# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import requests
import logging

log = logging.getLogger("LIMS Fake Session")


class FakeSession(requests.Session):

    @staticmethod
    def _noop():
        pass

    def __init__(self):
        super(FakeSession, self).__init__()

    def request(self, method, url, params=None, data=None, **kwargs):
        if method.upper() == "GET" or (method.upper() == "POST" and url.endswith('/batch/retrieve')):
            if params:
                log.info("Sending real %s %s\n\tParams: %s\n", method.upper(), url, params)
            else:
                log.info("Sending real %s %s", method.upper(), url)
            return super(FakeSession, self).request(method, url, params, data, **kwargs)
        else:
            if params:
                log.info(
                    "%s %s\n\tParams: %s\n\tData:\n%s\nEOR\n",
                    method.upper(), url, params, data.getvalue() if hasattr(data, 'getvalue') else data
                )
            else:
                log.info(
                    "%s %s\n%s\nEOR\n",
                    method.upper(), url, data.getvalue() if hasattr(data, 'getvalue') else data
                )

            empty_response = requests.Response()
            empty_response.status_code = 200

            if method.upper() == "PUT":
                # just copy it
                if hasattr(data, 'read'):
                    empty_response._content = data.read()
                else:
                    empty_response._content = data
            else:
                # should probably do something useful here
                log.info("Probably causing a problem by returning <nothing/> as %s fake response." % method)
                empty_response._content = "<nothing/>"
            empty_response.close = self._noop
            return empty_response
