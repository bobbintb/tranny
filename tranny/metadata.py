# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from sqlalchemy import or_
from sqlalchemy.exc import DBAPIError
from tranny import tasks
from tranny import constants
from tranny import exceptions
from tranny.app import Session
from tranny.datastore import get_genre, get_person_imdb
from tranny.service import trakt
from tranny.service import imdb
from tranny.util import raise_unless
from tranny.models import Show, Episode, Movie

log = logging.getLogger(__name__)


def update_media_info(release_key):
    tasks.add_task(tasks.Task(update_metadata, release_key))


def update_metadata(release_key):
    media_info = update_trakt(release_key)
    if media_info:
        media_info = update_imdb(media_info=media_info)
    return media_info


def update_imdb(media_info=None, release_key=None):
    session = Session()
    try:
        if media_info.imdb_id:
            movie_info = imdb.get_movie(media_info.imdb_id)
            if movie_info:
                media_info.imdb_score = movie_info['rating']
                media_info.imdb_votes = movie_info['votes']
                media_info.cover_url = movie_info['cover_url']
                for director in movie_info.get('director', []):
                    person = get_person_imdb(session, director['person_id'], name=director['name'])
                    if not person in media_info.directors:
                        media_info.directors.append(person)
                for cast_member in movie_info.get('cast', []):
                    person = get_person_imdb(session,
                                             cast_member['person']['person_id'],
                                             name=cast_member['person']['name'])
                    if not person in media_info.cast:
                        media_info.cast.append(person)
        session.commit()
    except DBAPIError:
        session.rollback()
    except exceptions.ApiError as e:
        log.warn(e.message)
    return media_info


def update_trakt(release_key):
    """

    :param release_key:
    :type release_key: BaseReleaseKey|TVReleaseKey|TVDailyReleaseKey|MovieReleaseKey
    """
    session = Session()
    media_info = None

    try:
        if release_key.media_type == constants.MEDIA_TV:
            if release_key.daily:
                info = trakt.show_episode_summary_daily(
                    release_key.name, release_key.day, release_key.month, release_key.year
                )
            else:
                info = trakt.show_episode_summary(release_key.name, release_key.season, release_key.episode)
            raise_unless(info, exceptions.ApiError, "Failed to fetch metadata for: {}".format(release_key))
            media_info = _update_trakt_tv(session, info)
        elif release_key.media_type == constants.MEDIA_MOVIE:
            info = trakt.movie_summary(release_key.name)
            raise_unless(info, exceptions.ApiError, "Failed to fetch metadata for: {}".format(release_key))
            media_info = _update_trakt_movie(session, info)
        else:
            return None
        session.commit()
    except DBAPIError as e:
        log.exception("Error querying media info")
        session.rollback()
    except exceptions.ApiError as e:
        log.warn(e.message)
    except Exception as e:
        log.exception("Could not update trakt info")
    return media_info


def _update_trakt_tv(session, info, update_show=True):
    """ Fetch trakt info and create or update the model instance with
    the latest API data available.

    :param session:
    :type session: sqlalchemy.orm.session.Session
    :param info: API response dict from trakt
    :type info: dict
    :return: Updated episode instance ready to be committed
    :rtype: Episode
    """
    show_args = Show.build_model_or_args(Show.external_keys, info.get('show', {}))
    show = session.query(Show).filter(or_(*show_args)).first()
    if not show:
        show = Show()
        session.add(show)
    if update_show or not show.show_id:
        show.update_properties(trakt.show_properties_map, info.get('show', {}))
        show.update_genres(session, info.get('show', {}).get('genres'))
    episode_args = Episode.build_model_or_args(Episode.external_keys, info.get('episode', {}))
    episode = session.query(Episode).filter(or_(*episode_args)).first()
    if not episode:
        episode = Episode()
        session.add(episode)
    episode.update_properties(trakt.episode_property_map, info.get('episode', {}))
    if not episode in show.episodes:
        show.episodes.append(episode)
    return episode


def _update_trakt_movie(session, info):
    movie_args = Movie.build_model_or_args(Movie.external_keys, info)
    movie = session.query(Movie).filter(or_(*movie_args)).first()
    if not movie:
        movie = Movie()
        session.add(movie)
    movie.update_properties(trakt.movie_property_map, info)
    movie.update_genres(session, info.get('genres', {}))
    return movie



