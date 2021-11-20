import abc
from functools import cached_property

import bs4
import requests
import typing as t
from housing_scraping_nl import headers, utils


class ScraperBase(abc.ABC):
    """Base class for scraping.

    Parameters
    ----------
    url : str
        URL of the page to be scraped.
    header_creator : headers.HeaderCreator
        Class to generate headers, containing settings for accessing the web page.
    """

    def __init__(self, url: str, header_creator: headers.HeaderCreator):
        self.url = url
        self.header_creator = header_creator

    @property
    def html_soup(self) -> bs4.BeautifulSoup:
        """Return a BeautifulSoup instance of the page's HTML source code."""
        # Set the cookie policy on the Requests session in order to reject cookies
        s = requests.Session()
        s.cookies.set_policy(utils.BlockAll())

        page = requests.get(self.url,
                            headers=self.header_creator())
        return bs4.BeautifulSoup(page.content, 'html.parser')


class ResultsScraper(ScraperBase):
    """Class to scrape one or multiple pages of search results, containing multiple listings."""

    @abc.abstractmethod
    def get_all_listing_urls(self) -> t.List[str]:
        """Get the URLs of all the listings in the page as a list."""
        pass

    @cached_property
    @abc.abstractmethod
    def number_of_pages(self) -> int:
        """Return the number of pages in the search results."""

        pass

    @abc.abstractmethod
    def scrape_all_listings(self) -> t.List[t.Dict[str, t.Any]]:
        """Scrape all listings for information."""

        pass


class ListingsPageScraper(ScraperBase):
    """Class to scrape results from a single page of search results."""

    @abc.abstractmethod
    def get_all_listing_urls(self) -> t.List[str]:
        """Get the URLs of all the listings in the results page as a list."""
        pass


class ListingScraper(ScraperBase):
    """Class to scrape a single listing page."""

    @abc.abstractmethod
    def get_title(self) -> str:
        """Get the title of the listing."""
        pass

    @abc.abstractmethod
    def get_photo_src(self) -> t.Optional[str]:
        """Get the source URL of the main listing's photo, if found."""

        pass

    @abc.abstractmethod
    def get_postal_code(self) -> t.Optional[str]:
        """Get the postal code of the listing, if found."""
        pass

    @abc.abstractmethod
    def get_agent_name(self) -> str:
        """Get the name of the agency responsible for the listing."""

        pass

    @abc.abstractmethod
    def get_agent_image_src(self) -> t.Optional[str]:
        """Get the source URL of the logo of the agency, if found."""

        pass

    @abc.abstractmethod
    def get_agent_link(self) -> t.Optional[str]:
        """Get the URL of the page of the agency, if found."""

        pass

    @abc.abstractmethod
    def get_description_text(self) -> t.Optional[str]:
        """Get the description of the listing as a string."""

        pass

    @abc.abstractmethod
    def get_all_info(self) -> t.Dict[str, t.Any]:
        """Get all the information of the listing as a dictionary."""

        pass
