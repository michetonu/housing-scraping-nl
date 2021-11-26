import abc
import json
import os
import typing as t
import random
from collections import OrderedDict
from functools import cached_property

from fake_useragent import UserAgent

from housing_scraping_nl import utils


class HeaderCreator(abc.ABC):
    """Base class for creating headers.

    The headers are returned by simply calling the class.
    >>> headers = HeaderCreator()
    """

    @abc.abstractmethod
    def __call__(self):
        pass


class FundaHeaderCreator(HeaderCreator):
    """Class to create headers to scrape Funda.

    Funda needs more complex headers in order to not appear as a scraper. For this
    reason, we get a random element from a list of headers stored in `headers.json`,
    which can be expanded at will.

    Usage:
    >>> headers = FundaHeaderCreator()
    """

    @cached_property
    def _headers_list(self) -> t.List[dict]:
        """Load the content of the json headers file as a dict."""
        with open(
            os.path.join(utils.SRC_PATH, "..", "resources", "headers.json"), "r"
        ) as headers_f:
            return json.load(headers_f)

    @property
    def _headers(self) -> t.List[OrderedDict]:
        """Return the headers in an ordered dict.

        See: https://dev.to/dimitryzub/how-to-reduce-chance-being-blocked-while-web-scraping-search-engines-1o46#ordered_headers
        """

        ordered_headers_list = []
        for headers in self._headers_list:
            h = OrderedDict()
            for header, value in headers.items():
                h[header] = value
                ordered_headers_list.append(h)
        return ordered_headers_list

    def __call__(self):
        return random.choice(self._headers)


class ParariusHeaderCreator(HeaderCreator):
    """Class to create headers to scrape Pararius.

    For Pararius, it is sufficient to get a random user agent using the fake_useragent
    package.

    Usage:
    >>> headers = ParariusHeaderCreator()
    """

    def __call__(self):
        ua = UserAgent()
        return {"User-Agent": str(ua.random)}
