import psycopg2
from psycopg2 import connect, OperationalError, errorcodes, errors

conn = psycopg2.connect(dbname="movieinfo",
                        port="5432",
                        host="localhost",
                        user="postgres",
                        password="1234")


def findExistingMovie(listId):
    cur = conn.cursor()
    sql = """SELECT array_agg(tmdbid) FROM links WHERE tmdbid = ANY(%s);"""
    cur.execute(sql, (listId,))
    existingIds = cur.fetchone()[0]
    if existingIds is None:
        existingIds = []
    missingIds = set(listId) - set(existingIds)
    object = {
        "existingIds": existingIds,
        "missingIds": missingIds
    }
    cur.close()
    return object


def countMovieEntriesInRating(movieIdList):
    cur = conn.cursor()
    countMovies = []
    for item in movieIdList:
        sql = """SELECT COUNT(*) FROM ratings2 WHERE "movieId" = %s"""
        cur.execute(sql, (item,))
        countMovies.append(cur.fetchone()[0])
    cur.close()
    return countMovies


def addNewValuesInMovieAndLink(missingIds, movies):
    cur = conn.cursor()
    sql = """SELECT "movieId" FROM movies ORDER BY "movieId" DESC LIMIT 1;"""
    cur.execute(sql)
    lastId = cur.fetchone()[0]
    cur.close()

    cur = conn.cursor()
    for el in missingIds:
        for item in movies.movieInfo:
            if (item.tmdbId == el):
                lastId += 1
                sql = """INSERT INTO movies ("movieId", "title", "genres") VALUES (%s, %s, %s)"""
                cur.execute(sql, (lastId, item.name, item.genre))
                conn.commit()
                sql = """INSERT INTO links ("movieid", "tmdbid") VALUES (%s, %s)"""
                cur.execute(sql, (lastId, item.tmdbId))
                conn.commit()
    cur.close()


def getMovieIdByTmdbId(idList):
    cur = conn.cursor()
    movieId = []
    for item in idList:
        sql = """SELECT "movieid" FROM public.links  WHERE "tmdbid" = %s;"""
        cur.execute(sql, (item,))
        movieId.append(cur.fetchone()[0])
    cur.close()
    return movieId

def findRatingByVoteAndMovie(userRating, returnCount=False):
    cur = conn.cursor()
    sql = """SELECT COUNT(*) FROM public.ratings2  where "movieId" = %s and "userId" = %s"""
    if(returnCount):
        sql = """SELECT * FROM public.ratings2  where "movieId" = %s and "userId" = %s"""
    cur.execute(sql, (userRating.movieId, userRating.userId))
    ratingList = cur.fetchone()
    cur.close()
    return ratingList

def deleteRatingValue(userRating):
    cur = conn.cursor()
    sql = """DELETE FROM public.ratings2  where "movieId" = %s and "userId" = %s"""
    cur.execute(sql, (userRating.movieId, userRating.userId))
    conn.commit()
    cur.close()

def setNewUserRating(userRating):
    if(findRatingByVoteAndMovie(userRating)[0] > 0):
        deleteRatingValue(userRating)
    cur = conn.cursor()
    sql = """INSERT INTO ratings2 ("userId", "movieId", "rating", "timestamp") VALUES (%s, %s, %s, %s)"""
    cur.execute(sql, (userRating.userId, userRating.movieId, userRating.rating, userRating.timestamp))
    conn.commit()
    cur.close()
