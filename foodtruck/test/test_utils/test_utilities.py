# -*- encoding: utf-8 -*-

import unittest

from foodtruck.utils import utilities
from foodtruck.test import FoodTruckTestCase
from foodtruck.utils.errors import HttpRequestFailedError
from foodtruck.utils.errors import HttpRequestError


class TestUtilities(FoodTruckTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

    def tearDown(self):
        pass

    def test_http_get(self):
        """Test http_get return 200."""
        response = utilities.http_get(self.http_get_good_url)
        self.assert_equal(response.status_code, 200)

    def test_http_get_return_http_request_error(self):
        """Test http_get raises HttpRequestError"""
        error = HttpRequestError(self.http_get_exception, 'some reason')
        self.assert_raise_error(
            error, utilities.http_get,
            self.http_get_exception
        )
