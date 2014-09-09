# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from tranny import tasks, constants, models
from tranny.app import Session
from tranny.service import trakt


def update_media_info(download):
    tasks.add_task(tasks.Task(update_trakt, download))


def update_trakt(release_key):
    """

    :param release_key:
    :type release_key: BaseReleaseKey|TVReleaseKey|TVDailyReleaseKey|MovieReleaseKey
    """
    session = Session()
    if release_key.media_type == constants.MEDIA_TV:
        info = trakt.show_episode_summary(
            release_key.name,
            release_key.season,
            release_key.episode)
        _update_trakt_tv(session, release_key, info)


def _update_trakt_tv(session, release_key, info):
    media_info = models.MediaInfo()

