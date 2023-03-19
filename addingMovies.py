import psycopg2
from psycopg2 import connect, OperationalError, errorcodes, errors

POSTGRESQL_HOSTS = 'postgresql://postgres:1234@localhost:5432/movieinfo'
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


def addNewValuesInMovieAndLink(missingIds, movies):
    cur = conn.cursor()
    sql = """SELECT "movieId" FROM movies ORDER BY "movieId" DESC LIMIT 1;"""
    cur.execute(sql)
    lastId = cur.fetchone()[0]
    cur.close()

    cur = conn.cursor()
    for el in missingIds:
        for item in movies.movieInfo:
            if (item.movieId == el):
                lastId += 1
                sql = """INSERT INTO movies ("movieId", "title") VALUES (%s, %s)"""
                cur.execute(sql, (lastId, item.name))
                conn.commit()
                sql = """INSERT INTO links ("movieid", "tmdbid") VALUES (%s, %s)"""
                cur.execute(sql, (lastId, item.movieId))
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


def setNewUserRating(userRating):
    cur = conn.cursor()
    sql = """INSERT INTO ratings ("userId", "movieId", "rating", "timestamp") VALUES (%s, %s, %s, %s)"""
    try:
        cur.execute(sql, (userRating.userId, userRating.movieId, userRating.rating, userRating.timestamp))
        conn.commit()
        cur.close()
    except errors.InFailedSqlTransaction as err:
        print_psycopg2_exception(err)
