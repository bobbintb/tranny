from tranny import config

# Try and load imdb
try:
    import imdb
except ImportError:
    imdb = False

# Try and load themoviedb
try:
    from tranny import tmdb

    _tmdb_api_key = config.get("themoviedb", "api_key")
    tmdb.configure(_tmdb_api_key)
except ImportError:
    tmdb = False


def get_score(title, precision=1):
    score = []
    if imdb:
        score.append(get_imdb_score(title))
    if tmdb:
        score.append(get_tmdb_score(title))
    return round(sum(score) / float(len(score)), precision)


def get_imdb_info(title):
    i = imdb.IMDb()
    search_result = i.search_movie(title, results=1)
    if not search_result:
        return None
    result = search_result[0]
    i.update(result)
    return result


def get_imdb_score(title):
    info = get_imdb_info(title)
    if info:
        return info['rating']
    return None


def get_tmdb_info(title):
    result = False
    search_result = tmdb.Movies(title, limit=True)
    for movie in search_result.iter_results():
        result = movie
        break
    return result


def get_tmdb_score(title):
    info = get_tmdb_info(title)
    rating = info['vote_average']
    return rating
