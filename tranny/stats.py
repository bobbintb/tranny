# -*- coding: utf-8 -*-
"""
Functions used to retrieve statistics from historical data.
"""

from collections import Counter
from tranny import app
from tranny import datastore
from tranny.app import Session


def count_totals(records, key_getter):
    """ Get the download totals for each provider registered in the database

    :param key_getter: Function used to determine the key of the object
    :type key_getter: callable
    :param records: list of history records
    :type records: tranny.models.Base[]
    :return: Dict with totals for each key corresponding to a providers name
    :rtype: dict[]
    """
    counts = Counter()
    for r in records:
        counts[key_getter(r)] += 1
    return counts


def provider_type_counter(records):
    """

    :param records:
    :type records: tranny.models.Download[]
    :return:
    :rtype:
    """
    rss_feeds = [name.split("_")[1] for name in app.config.find_sections("rss_")]
    providers = [name.split("_")[1] for name in app.config.find_sections("provider_")]
    counter = Counter()
    for record in records:
        # TODO fix with joined value
        source_name = record.source.source_name.lower()
        if source_name in rss_feeds:
            counter['RSS'] += 1
        elif source_name in providers:
            counter["API"] += 1
        elif source_name == "watch":
            counter["Watch"] += 1
        elif source_name == "web":
            counter['WebUI'] += 1
        else:
            counter['Unknown'] += 1
    return counter
