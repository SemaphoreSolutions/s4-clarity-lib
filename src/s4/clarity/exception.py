# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity import ETree


class ClarityException(Exception):
    """
    Exceptions that are returned as XML from Clarity LIMS.
    """
    def __init__(self, msg):
        super(ClarityException, self).__init__(msg)
        self.request_body = None

    @classmethod
    def raise_if_present(cls, response, data=None, username=None):
        """
        :type response: requests.Response
        :type data: any
        :type username: str
        """
        if cls.is_redirect(response):
            raise cls("Redirects are disabled, verify Clarity URI. Did you use http instead of https?")

        if cls.is_authentication_error(response):
            raise ClarityAuthenticationException("Password or username incorrect -- user '%s'" % username)

        # TODO detect when a user is authenticated but not authorized
        # a 'Forbidden' message is returned in the case when your
        # password is correct but you don't have API access, for example.

        cls.raise_on_exception(response, data)

        # this does nothing if it's 200 OK
        response.raise_for_status()

    @staticmethod
    def is_redirect(response):
        return response.status_code == 301

    @staticmethod
    def is_authentication_error(response):
        return response.status_code == 401

    @staticmethod
    def is_response_exception(response):
        return "<exc:exception" in response.text

    @classmethod
    def raise_on_exception(cls, response, data=None):

        # Make sure we are an exception, if not carry on
        if not cls.is_response_exception(response):
            return

        root = ETree.XML(response.content)
        try:
            msg = root.find('message').text
        except AttributeError:
            msg = "No message provided by Clarity."
        try:
            msg += "\nSuggested actions: " + root.find('suggested-actions').text
        except AttributeError:
            # no suggested-actions
            pass
        extra = root.get('category')
        if extra is not None:
            msg += "\nException category: " + extra
        extra = root.get('code')
        if extra is not None:
            msg += "\nException code: " + extra
        if "File does not exist" in msg:
            raise FileNotFoundException(msg)
        else:
            instance = cls(msg)
            instance.request_body = data.decode("UTF-8") if isinstance(data, bytes) else data
            raise instance


class ClarityAuthenticationException(ClarityException):
    pass


class FileNotFoundException(ClarityException):
    pass
