# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from sqlalchemy import or_
from sqlalchemy.exc import DBAPIError
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
        info = trakt.show_episode_summary(release_key.name, release_key.season, release_key.episode)
        _update_trakt_tv(session, release_key, info)
    try:
        session.commit()
    except DBAPIError:
        session.rollback()


def _update_trakt_tv(session, release_key, info):
    """

    :param session:
    :type session: sqlalchemy.orm.session.Session
    :param release_key:
    :type release_key:
    :param info:
    :type info:
    :return:
    :rtype:
    """
    show_args = []
    for key in ['tvrage_id', 'tvdb_id', 'imdb_id']:
        value = info.get('show', {}).get(key, None)
        if value:
            show_args.append(getattr(models.Show, key) == value)
    show = session.query(models.Show).filter(or_(*show_args)).first() if show_args else None
    if not show:
        show = models.Show()
        for model_prop, api_prop in trakt.show_properties_map:
            api_value = info.get('show', {}).get(api_prop, None)
            if not api_value:
                continue
            setattr(show, model_prop, api_value)
        session.add(show)
    episode_args = []
    for key in ['tvdb_id', 'imdb_id']:
        value = info.get('episode').get(key, None)
        if value:
            episode_args.append(getattr(models.Episode, key) == value)
    episode = session.query(models.Episode).filter(or_(*episode_args)).first()
    if not episode:
        episode = models.Episode()
        session.add(episode)
    for model_prop, api_prop in trakt.episode_property_map:
        api_value = info.get('episode', {}).get(api_prop, None)
        if not api_value:
            continue
        setattr(episode, model_prop, api_value)
    if not episode in show.episodes:
        show.episodes.append(episode)
    return episode



