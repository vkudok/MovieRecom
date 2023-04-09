from fastapi import FastAPI, Body, status
from collaborativeFiltering import trainCollModel, collaborativeRecom
from movieService import setNewUserRating, findRatingByVoteAndMovie, getMovieIdByTmdbId, addNewValuesInMovieAndLink, findExistingMovie
from contentBasedFiltering import contentBasedRecom
from index import recommendationDefine
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from movieService import countMovieEntriesInRating
import time

class MovieType(BaseModel):
    name: str
    genre: str
    tmdbId: int

class MovieInfoType(BaseModel):
    movieInfo: List[MovieType]


class RatingType(BaseModel):
    userId: str
    movieId: int
    rating: float
    timestamp: str


class UserRatingType(BaseModel):
    userId: str
    movieId: int

app = FastAPI()

origin = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

@app.post("/findMovieIdByTmdbId")
async def find(movies: MovieInfoType = Body()):
    listId = []
    for item in movies.movieInfo:
        listId.append(item.tmdbId)
    object = findExistingMovie(listId)
    if (len(object['missingIds'])):
        addNewValuesInMovieAndLink(object['missingIds'], movies)
    movieListIds = getMovieIdByTmdbId(listId)
    return movieListIds


@app.post("/setNewFilms")
async def find(movies: MovieInfoType = Body()):
    listId = []
    for item in movies.movieInfo:
        listId.append(item.tmdbId)
    object = findExistingMovie(listId)
    if (len(object['missingIds'])):
        addNewValuesInMovieAndLink(object['missingIds'], movies)
        trainCollModel()
    return object

@app.post("/getMovieIdByTmdbId")
async def find2(listId: List[int] = Body()):
    movieListIds = getMovieIdByTmdbId(listId)
    return movieListIds

@app.post("/trainCollModel")
async def find():
    trainCollModel()
    return {"trainCollModel": "trainCollModel"}

@app.post("/countMovieEntriesInRating")
async def countMovie(tmdbId):
    tmdbIdList = []
    tmdbIdList.append(tmdbId)
    movieIdList = getMovieIdByTmdbId(tmdbIdList)
    count = countMovieEntriesInRating(movieIdList)[0]
    return {"count": count}

@app.post("/setMovieRating")
async def setRating(userRating: RatingType = Body()):
    setNewUserRating(userRating)
    return {"message": 'Add Rating'}\

@app.post("/findRating")
async def findRating(userRating: UserRatingType = Body()):
    result = findRatingByVoteAndMovie(userRating, True)
    if(result is not None):
        return result[0]
    else:
        return result

@app.post("/getRecom")
async def getRecom(tmdbId, valueNumber=5):
    recom = recommendationDefine(int(tmdbId), int(valueNumber))
    return {"recommendation": recom}

@app.get("/content_recom")
async def content(movieId, valueNumber=5):
    start = time.time()
    recom = contentBasedRecom(int(movieId), int(valueNumber))
    end = time.time()
    return {"recommendation": recom, "time": end - start}


@app.get("/coll_recom")
async def coll_recom(movieId, valueNumber=5):
    recom = collaborativeRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}
