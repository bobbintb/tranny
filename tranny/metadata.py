# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from tranny import tasks, constants
from tranny.service import trakt


def update_media_info(download):
    tasks.add_task(tasks.Task(update_trakt, download))


def update_trakt(release_key):
    """

    :param release_key:
    :type release_key: tranny.datastore.BaseReleaseKey
    """
    if release_key.media_type == constants.MEDIA_TV:
        info = trakt.show_episode_summary()


