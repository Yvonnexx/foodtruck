# -*- encoding: utf-8 -*-

import unittest
import json
import os
import foodtruck

from scipy.spatial import kdtree
from flask.ext.cache import Cache

from foodtruck import app
from foodtruck.src import location
from foodtruck.utils import utilities
from foodtruck.utils.errors import HttpRequestError
from foodtruck.utils.errors import InvalidValueError
from foodtruck.utils.constants import SF_DATA_API
from foodtruck.utils.constants import CACHE_KEY_KD_TREE_ETAG


class FoodTruckTestCase(unittest.TestCase):
    """Base class for all FoodTruck test cases."""

    http_get_good_url = 'http://good.url.com'
    http_get_return_404_url = 'http://should.return.404.com'
    http_get_exception = 'http://should.raise.exception.com'
    sf_data_api_invalid_coordinate = 'http://invalid.coord.com'
    # Use this etag to force http_get return 304
    etag = '672800a386f99c6a306fc181d5ca3d3f'
    # Use this etag for all other cases
    non_match_etag = '2f8a1a799e129a8af143c00a500cb04'

    def setUp(self):
        from flask import Flask
        self.testapp = Flask('test-app')
        self.app = app.test_client()
        self.cache = Cache(self.testapp, config={'CACHE_TYPE': 'simple'})

        self.real_requests = utilities.requests
        self.real_cache = location.cache
        utilities.requests = MockRequests()
        location.cache = self.cache

    def tearDown(self):
        utilities.requests = self.real_requests
        location.cache = self.real_cache
        self.cache.clear()

    def get_kdtree(self):
        """Build a mocked KD-Tree."""
        all_foodtrucks, points = [], []
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        dir = cur_dir +  '/fixtures/foodtrucks.json'

        with open(dir, 'r') as f:
            all_foodtrucks = json.load(f)

        for foodtruck in all_foodtrucks:
            if 'x' in foodtruck and 'y' in foodtruck:
                try:
                    x = float(foodtruck['x'])
                except ValueError:
                    raise InvalidValueError('x', foodtruck['x'])
                try:
                    y = float(foodtruck['y'])
                except ValueError:
                    raise InvalidValueError('y', foodtruck['y'])
                point = (x, y)
                points.append(point)
        kd_tree = kdtree.KDTree(points)

        return kd_tree

    def assert_is_json(self, obj):
        try:
            json.loads(obj)
        except TypeError:
            raise AssertionError('%s is not a JSON object' % obj)

    def assert_is_none(self, obj, *args, **kwargs):
        return self.assertIsNone(obj, *args, **kwargs)

    def assert_is_not_none(self, obj, *args, **kwargs):
        return self.assertIsNotNone(obj, *args, **kwargs)

    def assert_equal(self, obj1, obj2, *args, **kwargs):
        return self.assertEqual(obj1, obj2, *args, **kwargs)

    def assert_true(self, true_value):
        return self.assertTrue(true_value)

    def assert_raise_error(self, exc, callable, *args, **kwargs):
        """Check if `callable` raises `exc`.

        :exc:      an instance of the exception you want to check
        :callable: the callable you want to call
        """
        try:
            callable(*args, **kwargs)
        except Exception, e:
            try:
                assert e.__class__ is exc.__class__
                assert e.message == exc.message
            except:
                raise AssertionError(
                    '{callable} did not raise {exception}'.format(
                        callable=callable.__name__,
                        exception=exc,
                    )
                )
        else:
            raise AssertionError(
                '{callable} did not raise {exception}'.format(
                    callable=callable.__name__,
                    exception=exc,
                )
            )


class MockRequests(object):
    """Mock requests package"""

    def get(self, url, *args, **kwargs):
        if url == FoodTruckTestCase.http_get_return_404_url:
            return MockRequestsResponseObject(
                url,
                status_code=404,
            )
        elif url == FoodTruckTestCase.http_get_exception:
            raise Exception('some reason')
        elif url == SF_DATA_API:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                if headers.get('If-None-Match') == FoodTruckTestCase.etag:
                    return MockRequestsResponseObject(
                        url,
                        status_code=304,
                        headers={'etag': FoodTruckTestCase.etag}
                    )
                else:
                    return MockRequestsResponseObject(
                        url,
                        status_code=200,
                        headers={'etag': FoodTruckTestCase.non_match_etag}
                    )
            return MockRequestsResponseObject(
                url,
                status_code=200,
            )
        else:
            return MockRequestsResponseObject(
                url,
                status_code=200,
            )


class MockRequestsResponseObject(object):
    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.status_code = kwargs.get('status_code', 500)
        self.headers = kwargs.get('headers', {})

    def __repr__(self):
        return '<MockRequestsResponseObject %s>' % self.url

    def json(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        if self.url == SF_DATA_API:
            dir = cur_dir + '/fixtures/foodtrucks.json'
            with open(dir, 'r') as f:
                return json.load(f)
        elif self.url == FoodTruckTestCase.sf_data_api_invalid_coordinate:
            dir = cur_dir + '/fixtures/foodtrucks_invalid_lat.json'
            with open(dir, 'r') as f:
                return json.load(f)
        else:
            return json.loads('{"json": "json"}')


def _get_tests():
    for cur, _, files in os.walk('.'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                module = cur.lstrip('./').replace('/', '.') + \
                    '.' + file.rstrip('.py')
                yield __import__(module, globals(), locals(), ['obj'], -1)


def _all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test in _get_tests():
        suite.addTests(loader.loadTestsFromModule(test))

    return suite


def main():
    try:
        unittest.main(__name__, defaultTest='_all_tests')
    except Exception, e:
        print 'Test failed: %s' % e
