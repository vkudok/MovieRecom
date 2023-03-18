from fastapi import FastAPI, Body, status
from trainModelRecom import setNewUserRating, getMovieIdByTmdbId, addNewValuesInMovieAndLink, findExistingMovie, \
    trainModel, collaborativeRecom
import csv
from typing import List
from pydantic import BaseModel


class MovieType(BaseModel):
    name: str
    movieId: int


class MovieInfoType(BaseModel):
    movieInfo: List[MovieType]


class RatingType(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: str


app = FastAPI()


@app.post("/findMovieIdByTableId")
async def find(movies: MovieInfoType = Body()):
    listId = []
    for item in movies.movieInfo:
        listId.append(item.movieId)
    object = findExistingMovie(listId)
    if (len(object['missingIds'])):
        addNewValuesInMovieAndLink(object['missingIds'], movies)
    movieListIds = getMovieIdByTmdbId(listId)
    trainModel()
    return {"movieListIds": movieListIds}


@app.post("/setMovieRating")
async def setRating(userRating: RatingType = Body()):
    setNewUserRating(userRating)
    return {"message": 'Add Rating'}


@app.get("/checkPSQL")
async def check():
    return {"message": 'checkPSQL'}


@app.get("/trainModel")
async def trainNew():
    trainModel()
    return {"message": 'trainModel'}


@app.get("/coll_recom")
async def coll_recom(movieId, valueNumber=5):
    recom = collaborativeRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}