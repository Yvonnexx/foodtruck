# -*- encoding: utf-8 -*-

import numpy
import logging
import cPickle
import utm

from flask import jsonify
from flask import request
from scipy.spatial import kdtree

from foodtruck import app
from foodtruck import cache
from foodtruck.utils.errors import Error
from foodtruck.utils.errors import InvalidValueError
from foodtruck.utils.errors import HttpRequestError
from foodtruck.utils.errors import HttpRequestFailedError
from foodtruck.utils.errors import BuildKDTreeError
from foodtruck.utils.errors import InternalAPIError
from foodtruck.utils.constants import SF_DATA_API
from foodtruck.utils.constants import CACHE_KEY_KD_TREE
from foodtruck.utils.constants import CACHE_KEY_KD_TREE_ETAG
from foodtruck.utils.constants import CACHE_KEY_FOODTRUCKS
from foodtruck.utils.utilities import http_get
from foodtruck.utils.utilities import pickle_kd_tree


logger = logging.getLogger(__name__)


def _build_kd_tree(api_path):
    """Build KD-Tree and cache foodtrucks.

    This function call `api_path` for foodtruck data, compile them and build
    KD-Tree from them. The compiled foodtruck data is then set into cache for
    later use.

    Arguments and return values:
    :api_path: should be `SF_DATA_API`

    :return:   an instance of kdtree.KDTree

    Exeptions:
    :InvalidValueError: when non-float-convertable latitude and longitude data
    is found in foodtruck data
    :BuildKDTreeError:  when failed on building KD-Tree
    """
    points, foodtrucks = [], []

    response = http_get(api_path)
    if response.status_code >= 400:
        raise HttpRequestFailedError(
            api_path,
            response.status_code,
        )

    etag = response.headers.get('etag')
    if etag:
        cache.set(CACHE_KEY_KD_TREE_ETAG, etag)
    else:
        logger.warning('Failed to get ETag from %s' % SF_DATA_API)

    all_foodtrucks = response.json()
    for foodtruck in all_foodtrucks:
        if foodtruck.get('status') == 'APPROVED' and \
                'latitude' in foodtruck and 'longitude' in foodtruck:
            try:
                lat = float(foodtruck['latitude'])
            except ValueError:
                raise InvalidValueError('lat', foodtruck['latitude'])
            try:
                lng = float(foodtruck['longitude'])
            except ValueError:
                raise InvalidValueError('longitude', foodtruck['longitude'])
            x, y, _, _ = utm.from_latlon(lat, lng)
            point = (x, y)
            points.append(point)
            foodtrucks.append(
                dict(
                    lot=foodtruck.get('lot'),
                    block=foodtruck.get('block'),
                    facility_type=foodtruck.get('facility_type'),
                    locationdescription=foodtruck.get('locationdescription'),
                    address=foodtruck.get('address'),
                    schedule=foodtruck.get('schedule'),
                    applicant=foodtruck.get('applicant'),
                    fooditems=foodtruck.get('fooditems'),
                    lat=foodtruck.get('latitude'),
                    lng=foodtruck.get('longitude'),
                )
            )
    cache.set(CACHE_KEY_FOODTRUCKS, foodtrucks)
    try:
        kd_tree = kdtree.KDTree(points)
    except Exception, e:
        raise BuildKDTreeError(e.message)

    return kd_tree


@app.route('/get_nearby_foodtrucks/<lat>/<lng>/<radius>',
           methods=['GET'])
def get_nearby_foodtrucks(lat, lng, radius):
    """Query all foodtrucks within `radius` miles from (`lat`, `lat`).

    This api takes a location(identified by its x and y coordinate), and a
    `radius`(the distance from the location), and finds all the foodtrucks
    with a distance less than or equal to `radius`, then returns all necessary
    information of the foodtrucks.

    Arguments and return values:
    :lat:      latitude of the location
    :lng:      longitude of the location
    :radius: the distance from the location
    """
    kd_tree = cached_tree = None
    nearby_foodtrucks = {}

    try:
        lat = float(lat)
    except ValueError:
        e = InvalidValueError('lat', lat)
        logger.error(e.message.get('error_message'))
        return jsonify(e.message)

    try:
        lng = float(lng)
    except ValueError:
        e = InvalidValueError('lng', lng)
        logger.error(e.message.get('error_message'))
        return jsonify(e.message)

    try:
        radius = float(radius)
    except ValueError:
        e = InvalidValueError('radius', radius)
        logger.error(e.message.get('error_message'))
        return jsonify(e.message)

    try:
        if radius <= 0:
            raise InvalidValueError('radius', radius)
    except InvalidValueError, e:
        logger.error(e.message.get('error_message'))
        return jsonify(e.message)

    try:
        # Get the KD-Tree from cache. If the key is found and is up to date,
        # use the KD-Tree in the cache, otherwise build the tree and set it
        # in the cache.
        if cache.get(CACHE_KEY_KD_TREE):
            cached_etag = cache.get(CACHE_KEY_KD_TREE_ETAG)
            response = http_get(
                SF_DATA_API,
                headers={'If-None-Match': cached_etag},
            )
            if response.status_code == 304:
                cached_tree = cache.get(CACHE_KEY_KD_TREE)
        if not cached_tree:
            kd_tree = _build_kd_tree(SF_DATA_API)
            cached_tree = pickle_kd_tree(kd_tree)
            cache.set(CACHE_KEY_KD_TREE, cached_tree)

        if not kd_tree:
            kd_tree = cPickle.loads(cached_tree)

        x, y, _, _ = utm.from_latlon(lat, lng)
        nearby_points = kd_tree.query_ball_point([x, y], radius)

        foodtrucks = cache.get(CACHE_KEY_FOODTRUCKS)
        if not foodtrucks:
            # TODO: call _build_kd_tree again to cache foodtrucks?
            logger.warning('No foodtruck found in cache.')

        l = len(foodtrucks)
        for i in nearby_points:
            if i > l:
                logger.warning('Foodtruck not found.')
                continue
            foodtruck = foodtrucks[i]
            lat = foodtruck.get('lat')
            lng = foodtruck.get('lng')
            if lat and lng:
                del foodtruck['lat']
                del foodtruck['lng']
                key = '%s:%s' % (lat, lng)
                nearby_foodtrucks[key] = foodtruck

        return jsonify(nearby_foodtrucks)
    except Error, e:
        logger.exception(e)

        return jsonify(e.message)
    except Exception, e:
        e = InternalAPIError(e)

        return jsonify(e.message)
