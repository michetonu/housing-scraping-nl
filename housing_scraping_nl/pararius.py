import json
import logging
import time
from datetime import datetime
from functools import cached_property

import bs4
from tqdm import tqdm
import typing as t

from housing_scraping_nl import config, utils
from housing_scraping_nl import headers
from housing_scraping_nl import scrapers

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


hc = headers.ParariusHeaderCreator()


class ParariusResultsScraper(scrapers.ResultsScraper):
    """Scraper for a set of results from Pararius."""

    def __init__(self, url: str, header_creator: headers.HeaderCreator = hc):
        super().__init__(url, header_creator)

    def get_all_listing_urls(self) -> t.List[str]:
        """Get the URLs of all the listings in the page as a list."""

        all_listings_urls = []
        for i in range(1, self.number_of_pages + 1):
            page_url = f"{self.url.split('?')[0]}/page-{i}"
            page_scraper = ParariusListingsPageScraper(page_url, hc)
            all_listings_urls.extend(page_scraper.get_all_listing_urls())
            # We sleep for some seconds in order to prevent being blacklisted
            time.sleep(config.SLEEP_SECONDS_BETWEEN_LISTINGS)

        logger.info(f"Number of listings to scrape: {len(all_listings_urls)}")
        return all_listings_urls

    @cached_property
    def number_of_pages(self) -> int:
        """Return the number of pages in the search results."""

        page_links = self.html_soup.find_all("a", {"class": "pagination__link"})
        page_numbers = [int(x.string) for x in page_links if x.string]
        return max(page_numbers)

    def scrape_all_listings(self):
        """Scrape all listings for information."""

        all_listing_urls = self.get_all_listing_urls()
        logger.info("Scraping all listings...")
        results = []
        for url in tqdm(all_listing_urls):
            listing = ParariusListingScraper(url, hc)
            try:
                results.append(listing.get_all_info())
            except Exception as e:
                # Broad exception on purpose – some listings might have
                # unforeseen errors, we might not want to stop the whole thing.
                logger.critical(e)
                continue
        logger.info("All listings scraped.")
        return results


class ParariusListingsPageScraper(scrapers.ListingsPageScraper):
    """Class to scrape results from a single page of Pararius search results."""

    def __init__(self, url: str, header_creator: headers.HeaderCreator = hc):
        super().__init__(url, header_creator)

    def get_all_listing_urls(self) -> t.List[str]:
        """Get the URLs of all the listings in the results page as a list."""

        page_soup = self.html_soup(self.url)
        listings = page_soup.find_all("h2", {"class": "listing-search-item__title"})
        return [listing.a.get("href") for listing in listings]


class ParariusListingScraper(scrapers.ListingScraper):
    """Class to scrape a single listing page from Pararius."""

    base_url = "https://pararius.com"

    def __init__(self, url: str, header_creator: headers.HeaderCreator = hc):
        super().__init__(url, header_creator)

    @staticmethod
    def _get_single_feature_value(feature_tag_name: bs4.element.Tag) -> t.Optional[str]:
        """Get the value of a single field from the listing's features.

        The value is the next sibling of <feature_tag_name>, sometimes
        directly as a `.string` attribute and sometimes in a div class.

        Parameters
        ----------
        feature_tag_name: bs4.element.Tag
            A BS4 tag holding the name of the feature.

        Returns
        -------
        type : Optional[str]
        """
        value_item = feature_tag_name.find_next_sibling()

        # If the sibling is a tag and has a string attribute, it means it's
        # already the feature value we are looking for
        if value_item.string:
            return str(value_item.string)

        # For more complex features, return the main description div
        # attribute.
        value = value_item.find("span", {"class": "listing-features__main-description"})
        if not value:
            return None
        return str(value)

    @staticmethod
    def _get_single_feature_name(feature_tag_name: bs4.element.Tag) -> str:
        """Get the name of a single field from the listing's features.

        The name is converted to snake case before returning it.

        Parameters
        ----------
        feature_tag_name: bs4.element.Tag
            A BS4 tag holding the name of the feature.

        Returns
        -------
        type : str
        """
        return utils.convert_to_snake_case(str(feature_tag_name.string))

    def _update_info(self, info: t.Dict[str, t.Any], feature_tag_name: bs4.element.Tag):
        feature_name = self._get_single_feature_name(feature_tag_name)
        feature_value = self._get_single_feature_value(feature_tag_name)
        if not feature_value:
            return
        if feature_name in info:
            # Some keys are duplicates, so we want to add them together
            # (e.g. Type of house could be present twice both as
            # "Apartment" and "Mezzanine")
            feature_value = info[feature_name] + ", " + feature_value
        info.update({feature_name: feature_value})

    def _get_listing_features_info(self) -> t.Dict[str, t.Any]:
        listing_features = self.html_soup.find_all(
            "dl", {"class": "listing-features__list"}
        )

        info = dict()
        for dlitem in listing_features:
            all_terms = dlitem.find_all("dt", {"class": "listing-features__term"})
            for feature_tag_name in all_terms:
                self._update_info(info, feature_tag_name)
        # Remove the 'Description' feature from the features list,
        # since it is not always reliable. The one from the listing main page
        # will be added in a separate step.
        info.pop("Description", None)

        return info

    def _add_extra_info(self):
        return {
            "description": self.get_description_text(),
            "postal_code": self.get_postal_code(),
            "scraped_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent": self.get_agent_name(),
        }

    def get_title(self) -> str:
        """Get the title of the listing."""

        title = self.html_soup.find_all(
            "h1", {"class": "listing-detail-summary__title"}
        )[0]
        return title.string.replace("For rent: ", "").replace(" in Amsterdam", "")

    def get_photo_src(self) -> t.Optional[str]:
        """Get the source URL of the main listing's photo, if found."""

        img = self.html_soup.find_all("img", {"class": "picture__image"})[0]
        return img.get("src")

    def get_postal_code(self) -> t.Optional[str]:
        """Get the postal code of the listing, if found."""

        data = json.loads(
            self.html_soup.find("script", type="application/ld+json").string
        )
        address = data.get("address")
        if not address:
            return None
        return address.get("postalCode")

    def get_agent_name(self) -> t.Optional[str]:
        """Get the name of the agency responsible for the listing."""

        listings = self.html_soup.find_all("a", {"class": "agent-summary__title-link"})
        if not listings:
            return None
        return listings[0].string

    def get_agent_image_src(self) -> t.Optional[str]:
        """Get the source URL of the logo of the agency, if found."""

        div = self.html_soup.find(
            "div", {"class": "picture picture--agent-detail-logo"}
        )
        if not div:
            return None
        pic = div.find("picture")
        image = pic.find("img", {"class": "picture__image"})
        return image.get("src")

    def get_agent_link(self) -> str:
        """Get the URL of the page of the agency, if found."""

        a = self.html_soup.find("a", {"class": "agent-summary__logo-link"})
        return f"{self.base_url}{a['href']}"

    def get_description_text(self) -> t.Optional[str]:
        """Get the description of the listing as a string."""

        description = self.html_soup.find(
            "div", {"class": "listing-detail-description__additional"}
        )
        return description.get_text().strip()

    def get_all_info(self) -> t.Dict[str, t.Any]:
        """Get all the information of the listing as a dictionary."""

        actual_listing_url = self.url
        # TODO check this
        # Some listing URLs do not seem to start with the right prefix
        if not actual_listing_url.startswith(self.base_url):
            actual_listing_url = f"{self.base_url}{actual_listing_url}"

        info = self._get_listing_features_info()
        extra_info = self._add_extra_info()
        info.update(extra_info)

        info["url"] = actual_listing_url

        return info


if __name__ == "__main__":
    pass
    # TODO
