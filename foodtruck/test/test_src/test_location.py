# -*- encoding: utf-8 -*-

import json

from scipy.spatial.kdtree import KDTree

from foodtruck import cache
from foodtruck.test import FoodTruckTestCase
from foodtruck.utils.errors import compose_message
from foodtruck.utils.errors import invalid_value_error
from foodtruck.utils.errors import InvalidValueError
from foodtruck.utils.errors import BuildKDTreeError
from foodtruck.utils.errors import HttpRequestFailedError
from foodtruck.src.location import _build_kd_tree
from foodtruck.utils.constants import SF_DATA_API
from foodtruck.utils.constants import CACHE_KEY_KD_TREE
from foodtruck.utils.constants import CACHE_KEY_KD_TREE_ETAG
from foodtruck.utils.utilities import pickle_kd_tree


class TestLocation(FoodTruckTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        self.url_get_nearby_ft = '/get_nearby_foodtrucks/{x}/{y}/{radius}'

    def tearDown(self):
        pass

    def test_build_kd_tree_success(self):
        """Test build KD-Tree succeed"""
        kd_tree = _build_kd_tree(SF_DATA_API)
        self.assert_true(isinstance(kd_tree, KDTree))

    def test_build_kd_tree_raises_http_request_failed_error(self):
        """Test build KD-Tree raises exception on api call returning 404."""
        error = HttpRequestFailedError(self.http_get_return_404_url, 404)
        self.assert_raise_error(
            error,
            _build_kd_tree,
            self.http_get_return_404_url,
        )

    def test_build_kd_tree_raises_invalid_value_error(self):
        """Test build KD-Tree raises exception on api call returning data
        that contains invalid x coordinate."""
        error = InvalidValueError('lat', 'lat')
        self.assert_raise_error(
            error,
            _build_kd_tree,
            self.sf_data_api_invalid_coordinate,
        )

    def test_build_kd_tree_set_etag(self):
        pass

    def test_get_nearby_foodtrucks_radius_less_than_zero(self):
        """Test calling get_nearby_foodtrucks raises exception when being
        passed a negative radius value."""
        radius = -.1
        api_url = self.url_get_nearby_ft.format(
            x=.1,
            y=.1,
            radius=radius,
        )
        response = self.app.get(api_url).data

        self.assert_is_json(response)
        response = json.loads(response)
        message = compose_message(
            invalid_value_error,
            var='radius',
            value=radius
        )
        self.assert_equal(response, message)

    def test_get_nearby_foodtrucks_raises_invalid_value_error(self):
        """Test calling get_nearby_foodtrucks with value that can't be
        converted to float."""
        radius = 'I_cannot_be_converted_to_string'
        api_url = self.url_get_nearby_ft.format(
            x=.1,
            y=.1,
            radius=radius,
        )
        response = self.app.get(api_url).data

        self.assert_is_json(response)
        response = json.loads(response)
        message = compose_message(
            invalid_value_error,
            var='radius',
            value=radius,
        )
        self.assert_equal(response, message)

    def test_get_nearby_foodtrucks_cache_hit_and_304(self):
        """Test calling get_nearby_foodtrucks hit cache and resource is not
        modified"""
        kd_tree = self.get_kdtree()
        cached_tree = pickle_kd_tree(kd_tree)
        self.cache.set(CACHE_KEY_KD_TREE, cached_tree)
        self.cache.set(CACHE_KEY_KD_TREE_ETAG, self.etag)

        api_url = self.url_get_nearby_ft.format(
            x=.1,
            y=.1,
            radius=.1,
        )
        response = self.app.get(api_url).data

    def test_get_nearby_foodtrucks_cache_hit_and_no_304(self):
        pass

    def test_get_nearby_foodtrucks_cache_miss(self):
        """Test get_nearby_foodtrucks cache miss"""
        self.assert_is_none(self.cache.get(CACHE_KEY_KD_TREE))
        self.assert_is_none(self.cache.get(CACHE_KEY_KD_TREE_ETAG))

        kd_tree = self.get_kdtree()
        cached_tree = pickle_kd_tree(kd_tree)

        api_url = self.url_get_nearby_ft.format(
            x=.1,
            y=.1,
            radius=.1,
        )
        response = self.app.get(api_url).data

        self.assert_is_not_none(self.cache.get(CACHE_KEY_KD_TREE))
        self.assert_is_not_none(self.cache.get(CACHE_KEY_KD_TREE_ETAG))
