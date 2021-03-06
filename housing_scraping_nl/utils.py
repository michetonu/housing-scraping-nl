import os
import re
from http import cookiejar

SRC_PATH = os.path.dirname(os.path.realpath(__file__))


class BlockAll(cookiejar.CookiePolicy):
    """Reject all cookies on the page automatically.

    Used as follows:
    >>> import requests
    >>> s = requests.Session()
    >>> s.cookies.set_policy(BlockAll())

    From: https://stackoverflow.com/questions/17037668/how-to-disable-cookie-handling-with-the-python-requests-library
    """

    return_ok = (
        set_ok
    ) = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


def convert_to_snake_case(to_convert: str) -> str:
    """Convert a string to snake case.

    >>> convert_to_snake_case("A String")
    'a_string'

    >>> convert_to_snake_case("AnotherString")
    'another_string'

    From:
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    Parameters
    ----------
    to_convert : str
        String to convert to snake case.

    Returns
    -------
    type : str
        String converted to snake case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', to_convert).lower()
