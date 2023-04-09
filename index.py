from enums import numMoviesInRating
from collaborativeFiltering import collaborativeRecom
from contentBasedFiltering import contentBasedRecom
from movieService import countMovieEntriesInRating, getMovieIdByTmdbId

def recommendationDefine(tmdbId, numRecom):
    tmdbIdList = []
    tmdbIdList.append(tmdbId)
    movieIdList = getMovieIdByTmdbId(tmdbIdList)
    count = countMovieEntriesInRating(movieIdList)[0]
    if (count < numMoviesInRating):
        return contentBasedRecom(movieIdList[0], numRecom)
    else:
        return collaborativeRecom(movieIdList[0], numRecom)
