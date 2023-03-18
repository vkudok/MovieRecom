from fastapi import FastAPI, Body, status
from trainModelRecom import getMovieIdByTmdbId, addNewValuesInMovieAndLink, findExistingMovie, trainModel, collRecom
import csv
from typing import List
from pydantic import BaseModel

class Movie(BaseModel):
    name: str
    movieId: int

class MovieInfo(BaseModel):
    movieInfo: List[Movie]

app = FastAPI()


@app.post("/findMovieIdByTableId")
async def find(movies: MovieInfo = Body()):
    listId = []
    for item in movies.movieInfo:
        listId.append(item.movieId)
    object = findExistingMovie(listId)
    if (len(object['missingIds'])):
        addNewValuesInMovieAndLink(object['missingIds'], movies)
    movieListIds = getMovieIdByTmdbId(listId)
    trainModel()
    return {"movieListIds": movieListIds}


@app.get("/checkPSQL")
async def check():
    return {"message": 'checkPSQL'}


@app.get("/trainModel")
async def trainNew():
    trainModel()
    return {"message": 'trainModel'}


@app.get("/coll_recom")
async def coll_recom(movieId, valueNumber=5):
    recom = collRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}


@app.get("/add_rating")
async def add_new():
    fields = ["612", "110", "4.0", "964982703"]
    with open(r'ratings.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    return {"message": 'Add Rating'}
