import json
import logging
import time
from datetime import datetime
from functools import cached_property

import bs4
from tqdm import tqdm
import typing as t

from housing_scraping_nl import config
from housing_scraping_nl import headers
from housing_scraping_nl import scrapers

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


header_creator = headers.ParariusHeaderCreator()


class ParariusWebsiteScraper(scrapers.ResultsScraper):
    def get_all_listing_urls(self) -> t.List[str]:
        all_listings_urls = []
        for i in range(1, self.number_of_pages + 1):
            page_url = f"{self.url.split('?')[0]}/page-{i}"
            page_scraper = ParariusListingsPageScraper(page_url, header_creator)
            all_listings_urls.extend(page_scraper.get_all_listing_urls())
            # We sleep for some seconds in order to prevent being seen as scrapers
            time.sleep(config.SLEEP_SECONDS_BETWEEN_LISTINGS)

        logger.info(f"Number of listings to scrape: {len(all_listings_urls)}")
        return all_listings_urls

    @cached_property
    def number_of_pages(self) -> int:
        page_links = self.html_soup.find_all("a", {"class": "pagination__link"})
        page_numbers = [int(x.string) for x in page_links if x.string]
        return max(page_numbers)

    def scrape_all_listings(self):
        all_listing_urls = self.get_all_listing_urls()
        logger.info("Scraping all listings...")
        results = []
        for url in tqdm(all_listing_urls):
            listing = ParariusListingScraper(url, header_creator)
            try:
                results.append(listing.get_all_info())
            except Exception as e:
                # Broad exception on purpose – some listings might have unforeseen errors,
                # we might not want to stop the whole thing.
                logger.critical(e)
                continue
        logger.info("All listings scraped.")
        return results


class ParariusListingsPageScraper(scrapers.ListingsPageScraper):
    def get_all_listing_urls(self) -> t.List[str]:
        page_soup = self.html_soup(self.url)
        listings = page_soup.find_all("h2", {"class": "listing-search-item__title"})
        return [listing.a.get('href') for listing in listings]


class ParariusListingScraper(scrapers.ListingScraper):
    @staticmethod
    def _get_single_feature_info(feature: bs4.element.ResultSet):
        name = feature.string
        value_item = feature.find_next_sibling()
        if value_item.string:
            return name, value_item.string

        value = value_item.find('div',
                                {'class': 'listing-features__main-description'}).string
        return name, value

    def _get_listing_features_info(self, listing_features: bs4.element.ResultSet) -> t.Dict[str, t.Any]:
        info = dict()
        for dlitem in listing_features:
            for feature in dlitem.find_all('dt', {'class': 'listing-features__term'}):
                feature_name, feature_value = self._get_single_feature_info(feature)
                if feature_name in info:
                    # Some keys are duplicates, so we want to add them together (e.g. Type of house
                    # could be present twice both as "Apartment" and "Mezzanine"
                    feature_value = info[feature_name] + ', ' + feature_value
                info.update({feature_name: feature_value})
        return info

    def get_title(self) -> str:
        title = self.html_soup.find_all("h1", {"class": "listing-detail-summary__title"})[0]
        return title.string.replace("For rent: ", "").replace(" in Amsterdam", "")

    def get_photo_src(self) -> t.Optional[str]:
        img = self.html_soup.find_all("img", {"class": "picture__image"})[0]
        return img.get('src')

    def get_postal_code(self) -> t.Optional[str]:
        data = json.loads(self.html_soup.find('script', type='application/ld+json').string)
        if 'address' not in data:
            return None
        return data['address'].get('postalCode')

    def get_agent_name(self) -> t.Optional[str]:
        listings = self.html_soup.find_all("a", {"class": "agent-summary__title-link"})
        if not listings:
            return None
        return listings[0].string

    def get_agent_image_src(self) -> t.Optional[str]:
        div = self.html_soup.find("div", {"class": "picture picture--agent-detail-logo"})
        if not div:
            return None
        pic = div.find('picture')
        image = pic.find('img', {"class": "picture__image"})
        return image.get('src')

    def get_agent_link(self) -> str:
        a = self.html_soup.find("a", {"class": "agent-summary__logo-link"})
        return f"https://pararius.com{a['href']}"

    def get_description_text(self) -> t.Optional[str]:
        description = self.html_soup.find("div", {"class": "listing-detail-description__additional"})
        return description.get_text()

    def get_all_info(self) -> t.Dict[str, t.Any]:
        actual_listing_url = self.url
        # TODO check this
        # Some listing URLs do not seem to start with the right prefix
        if not actual_listing_url.startswith('https://'):
            actual_listing_url = f'https://pararius.com{actual_listing_url}'

        listing_features = self.html_soup.find_all("dl", {"class": "listing-features__list"})

        info = self._get_listing_features_info(listing_features)

        # Remove the 'Description' feature from the features list,
        # since it is not always reliable. Add the one from the listing itself
        info.pop('Description', None)
        info['description'] = self.get_description_text()

        # Add extra features that need more processing
        info["url"] = actual_listing_url
        info['postal_code'] = self.get_postal_code()
        info['scraped_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info['agent'] = self.get_agent_name()
        return info


if __name__ == '__main__':
    pass
    # TODO
