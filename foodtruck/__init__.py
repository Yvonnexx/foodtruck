# -*- encoding: utf-8 -*-

import logging

from flask import Flask
from flask.ext.cache import Cache


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s '
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

from foodtruck.src import location
from foodtruck.web import main
