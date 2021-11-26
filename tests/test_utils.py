# -*- encoding: utf-8 -*-
"""Tests for the process utils.

Author: Michele Tonutti
Date: 2020-03-31
"""
import json
import logging
import os
import shutil
import unittest
from unittest.mock import patch

import requests

from housing_scraping_nl import utils


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_blockall(self):
        s = requests.Session()
        s.cookies.set_policy(utils.BlockAll())
        self.assertIsInstance(s.cookies.get_policy(), utils.BlockAll)

    def test_convert_to_snake_case(self):
        self.assertEqual(utils.convert_to_snake_case("A String"), "a_string")
        self.assertEqual(utils.convert_to_snake_case("AnotherString"), "another_string")
        self.assertEqual(utils.convert_to_snake_case("a String"), "a_string")
        self.assertEqual(utils.convert_to_snake_case("1234String"), "1234_string")
        self.assertEqual(utils.convert_to_snake_case("1234#$"), "1234#$")
        self.assertEqual(utils.convert_to_snake_case("a string"), "a_string")
        self.assertEqual(utils.convert_to_snake_case("A string"), "a_string")
