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
    @abc.abstractmethod
    def __call__(self):
        pass


class FundaHeaderCreator(HeaderCreator):
    @cached_property
    def _headers_list(self) -> t.List[dict]:
        with open(
            os.path.join(utils.SRC_PATH, "..", "resources", "headers.json"), "r"
        ) as headers_f:
            return json.load(headers_f)

    @property
    def _headers(self) -> t.List[OrderedDict]:
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
    def __call__(self):
        ua = UserAgent()
        return {"User-Agent": str(ua.random)}
