
# Current run state
from .exceptions import ConfigError

running = False

client = None
session = None
config = None
watcher = None
wait_time = 1

# Running services
services = []

# Running RSS Feeds
feeds = []

from app import create_app


def init_client():
    """ Initialize the torrent client being used to handle the torrent data retreived.

    :return:
    :rtype: TransmissionClient
    """
    global client
    if not client:
        enabled_client = config.get_default("general", "client", "transmission").lower()
        if enabled_client == "transmission":
            from tranny.client.transmission import TransmissionClient as TorrentClient
        elif enabled_client == "utorrent":
            from tranny.client.utorrent import UTorrentClient as TorrentClient
        else:
            raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
        client = TorrentClient(config)
    return client


def init_watcher():
    """ Start configured services

    :return:
    :rtype: FileWatchService
    """
    global watcher

    if not watcher:
        watcher = FileWatchService(config)
    return watcher





def init_webui(section_name="webui"):
    global config
    if config.getboolean(section_name, "enabled"):
        log.debug("WebUI enabled, starting.")
        hostname = config.get(section_name, "listen_host")
        port = config.getint(section_name, "listen_port")
        debug = config.getboolean(section_name, "enabled")
        web.start(listen_host=hostname, listen_port=port, debug=debug)
    else:
        log.debug("WebUI disabled, not starting.")


def start():
    """ Start up all the backend services of the application """
    init_config()
    init_logging()
    init_datastore()
    init_watcher()
    init_client()
    init_webui()
    reload_conf()


def reload_conf():
    """ Reload all services with new configuration settings

    :return:
    :rtype:
    """
    global config, feeds, services

    try:
        tmdb_api_key = config.get("themoviedb", "api_key")
        from tranny import tmdb

        tmdb.configure(tmdb_api_key)
    except:
        pass
    feeds = [RSSFeed(config, feed_section) for feed_section in config.find_sections("rss_")]
    service_list = [section for section in config.find_sections("service_") if config.getboolean(section, "enabled")]
    for service_name in service_list:
        from tranny.provider.broadcastthenet import BroadcastTheNet

        service = BroadcastTheNet(config, service_name)
        services.append(service)


def update_services(services):
    """ Update the provided services

    :param services: List of services
    :type services: TorrentProvider[]
    :return:
    :rtype:
    """
    for service in services:
        try:
            for torrent in service.find_matches():
                dl_path = config.get_download_path(torrent.section, torrent.release_name)
                res = client.add(torrent.torrent_data, download_dir=dl_path)
                if res:
                    log.info("Added release: {0}".format(torrent.release_name))
                    release_key = datastore.generate_release_key(torrent.release_name)
                    section = datastore.get_section(torrent.section)
                    source = datastore.get_source(service.name)
                    download = DownloadEntity(release_key, torrent.release_name, section.section_id, source.source_id)
                    session.add(download)
                    session.commit()
        except Exception as err:
            log.exception("Error updating service")


def update_rss(feeds):
    """ Update the provided RSS feeds

    :param feeds: Feeds to update
    :type feeds: TorrentProvider[]
    """
    for feed in feeds:
        try:
            for torrent in feed.find_matches():
                dl_path = config.get_download_path(torrent.section, torrent.release_name)
                res = client.add(torrent.torrent_data, download_dir=dl_path)
                if res:
                    log.info("Added release: {0}".format(torrent.release_name))
                    release_key = datastore.generate_release_key(torrent.release_name)
                    section = datastore.get_section(torrent.section)
                    source = datastore.get_source(feed.name)
                    download = DownloadEntity(release_key, torrent.release_name, section.section_id, source.source_id)
                    session.add(download)
                    session.commit()
        except Exception as err:
            log.exception("Error updating feed")


def run_forever():
    """ Run the server under a basic event loop """
    global feeds, config, watcher

    running = True
    try:
        while running:
            update_services(services)
            update_rss(feeds)
            sleep(1)
    except:
        pass
    finally:
        log.info("Exiting")
        web.stop()
        db.sync()
        watcher.stop()

from tranny.models import *

