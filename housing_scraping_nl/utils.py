import os
from http import cookiejar

SRC_PATH = os.path.dirname(os.path.realpath(__file__))


class BlockAll(cookiejar.CookiePolicy):
    """Reject all cookies on the page automatically.

    From: https://stackoverflow.com/questions/17037668/how-to-disable-cookie-handling-with-the-python-requests-library
    """
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
