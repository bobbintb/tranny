# -*- coding: utf-8 -*-
"""

"""

import logging
from dogpile.cache import make_region

log = logging.getLogger(__name__)

region = make_region()
cache_on_arguments = region.cache_on_arguments
cache_multi_on_arguments = region.cache_multi_on_arguments


def configure(config):
    """ Configure the dogpile.cache region instance with values from our config

    # Todo: dont hardcode this

    :param config: Application config instance
    :type config: Configuration
    """
    region.configure_from_config(
        {
            "cache.local.expiration_time": 3600,
            "cache.local.backend": "dogpile.cache.dbm",
            "cache.local.arguments.filename": config.cache_file
        },
        "cache.local."
    )


def invalidate():
    """ Wipe any existing cache file

    :return: Wipe status
    :rtype: bool
    """
    region.invalidate(True)
