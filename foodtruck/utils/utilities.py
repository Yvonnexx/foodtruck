# -*- encoding: utf-8 -*-

import requests
import cPickle

from scipy.spatial import kdtree
from foodtruck.utils.errors import HttpRequestError


def http_get(url, *args, **kwargs):
    # requests automatically sets Accept-Encoding header, which could stop
    # SF data api from returning ETag header. So disable it when it is not
    # explicitly set.
    if not kwargs.get('headers'):
        kwargs = {'headers': {'Accept-Encoding': ''}}
    elif not kwargs['headers'].get('Accept-Encoding'):
        kwargs['headers']['Accept-Encoding'] = ''
    try:
        response = requests.get(url, *args, **kwargs)
    except Exception, e:
        raise HttpRequestError(url, e)

    return response


def pickle_kd_tree(kd_tree):
    # This function is a workaround for pickling a recursive data structure
    # using cPickle.
    kdtree.node = kdtree.KDTree.node
    kdtree.leafnode = kdtree.KDTree.leafnode
    kdtree.innernode = kdtree.KDTree.innernode
    cached_tree = cPickle.dumps(kd_tree)

    return cached_tree
