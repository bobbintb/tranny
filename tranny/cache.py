# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
from os.path import join
from dogpile.cache import make_region

region = make_region()
cache_on_arguments = region.cache_on_arguments
cache_multi_on_arguments = region.cache_multi_on_arguments


def configure(config):
    """ Configure the dogpile.cache region instance with values from our config

    # Todo: dont hardcode this

    :param config:
    :type config: tranny.config.Configuration
    :return:
    :rtype:
    """
    region.configure_from_config(
        {
            "cache.local.expiration_time": 3600,
            "cache.local.backend": "dogpile.cache.dbm",
            "cache.local.arguments.filename": join(config.cache_path, "web_cache.dbm")
        },
        "cache.local."
    )


