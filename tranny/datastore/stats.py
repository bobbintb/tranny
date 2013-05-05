from collections import Counter
from tranny import get_config


class PieChart(Counter):
    def graph_data(self):
        return [{'label': section, "data": total} for section, total in self.most_common()]


def service_totals(records):
    """ Get the download totals for each provider registered in the database

    :param records: list of history records
    :type records: dict
    :return: Dict with totals for each key corresponding to a providers name
    :rtype: dict[]
    """
    data = [r['source'] for r in records]
    return PieChart(data).graph_data()


def section_totals(records):
    data = [r['section'].split("_")[1] for r in records]
    return PieChart(data).graph_data()


def service_type_totals(records):
    config = get_config()
    rss_feeds = [name.split("_")[1] for name in config.find_sections("rss_")]
    services = [name.split("_")[1] for name in config.find_sections("service_")]
    counter = Counter()
    for record in records:
        if record['source'] in rss_feeds:
            counter['RSS'] += 1
        elif record['source'] in services:
            counter["{0} (api)".format(record['source'])] += 1
        elif record['source'] == "watch":
            counter["Watch"] += 1
        else:
            counter['Unknown'] += 1
    section_data = PieChart(counter).graph_data()
    return section_data
