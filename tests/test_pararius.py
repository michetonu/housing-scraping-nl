import os
import unittest
from unittest.mock import patch

from housing_scraping_nl import pararius


class TestParariusBase(unittest.TestCase):
    def setUp(self) -> None:
        self.url = "http://fake-url"


class TestScrapersPararius(TestParariusBase):
    def setUp(self):
        super().setUp()
        self.scraper = pararius.ParariusListingScraper(url=self.url)
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                "test_listing_pararius.html",
            ),
            "r",
        ) as ff:
            self.html = ff.read()

    @patch("requests.get")
    def test_get_agent_image_src(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_agent_image_src()
        self.assertEqual(
            out,
            "https://media.pararius.nl/image/EA0000012000/EA0000012722/image/jpeg/120x260/Van_Huis_Uit_MakelaarsAmsterdamJanPieter-cf24_1.jpg",
        )

    @patch("requests.get")
    def test_get_agent_link(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_agent_link()
        self.assertEqual(
            out,
            "https://pararius.com/real-estate-agents/amsterdam/van-huis-uit-makelaars",
        )

    @patch("requests.get")
    def test_get_agent_name(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_agent_name()
        self.assertEqual(out, "Van Huis Uit Makelaars")

    @patch("requests.get")
    def test_get_all_info(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_all_info()
        expected_keys = [
            "rental_price",
            "offered_since",
            "status",
            "available",
            "deposit",
            "interior",
            "upkeep",
            "living_area",
            "plot_area",
            "volume",
            "type_of_house",
            "type_of_construction",
            "year_of_construction",
            "number_of_rooms",
            "number_of_bedrooms",
            "number_of_bathrooms",
            "number_of_floors",
            "balcony",
            "insulation",
            "heating",
            "energy_rating",
            "type_of_parking_facilities",
            "description",
            "postal_code",
            "scraped_timestamp",
            "agent",
            "url",
        ]
        self.assertListEqual(sorted(out.keys()), sorted(expected_keys))
        self.assertFalse(any(item is None for item in out.values()))

    @patch("requests.get")
    def test_get_description_text(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_description_text()
        self.assertTrue(out.startswith("Description"))

    @patch("requests.get")
    def test_get_photo_src(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_photo_src()
        self.assertEqual(
            out,
            "https://casco-media-prod.global.ssl.fastly.net/dd58755b-cf5d-52dd-a939-92e10c5a1468/3ae915461e53619adb4dd879b8e5c52f.jpg?width=600&auto=webp",
        )

    @patch("requests.get")
    def test_get_postal_code(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_postal_code()
        self.assertEqual(out, "1057CN")

    @patch("requests.get")
    def test_get_title(self, mock_request_getter):
        mock_request_getter.return_value.content = self.html

        out = self.scraper.get_title()
        self.assertEqual(out, "Apartment Hoofdweg 147 B")
