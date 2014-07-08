# -*- coding: utf-8 -*-
"""
Functions used to retrieve statistics from historical data.
"""
from __future__ import unicode_literals
from collections import Counter
from tranny import app, datastore


class PieChart(Counter):
    def graph_data(self):
        return [{'label': section, "data": total} for section, total in self.most_common()]


def service_totals(records):
    """ Get the download totals for each provider registered in the database

    :param records: list of history records
    :type records: tranny.models.DownloadEntity[]
    :return: Dict with totals for each key corresponding to a providers name
    :rtype: dict[]
    """
    return PieChart(datastore.get_source(source_id=r.source_id).source_name for r in records).graph_data()


def section_totals(records):
    data_set = (datastore.get_section(section_id=r.section_id).section_name.split("_")[1] for r in records)
    return PieChart(data_set).graph_data()


def service_type_totals(records):
    """

    :param records:
    :type records: tranny.models.DownloadEntity[]
    :return:
    :rtype:
    """
    rss_feeds = [name.split("_")[1] for name in app.config.find_sections("rss_")]
    services = [name.split("_")[1] for name in app.config.find_sections("service_")]
    counter = PieChart()
    for record in records:
        # TODO fix with joined value
        source_name = datastore.get_source(source_id=record.source_id).source_name
        if source_name in rss_feeds:
            counter['RSS'] += 1
        elif source_name in services:
            counter["{0} (api)".format(source_name)] += 1
        elif source_name == "watch":
            counter["Watch"] += 1
        else:
            counter['Unknown'] += 1
    return counter.graph_data()
