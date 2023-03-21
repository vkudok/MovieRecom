from fastapi import FastAPI, Body, status
from collaborativeFiltering import trainCollModel, collaborativeRecom
from movieService import setNewUserRating, getMovieIdByTmdbId, addNewValuesInMovieAndLink, findExistingMovie
from contentBasedFiltering import contentBasedRecom
from index import recommendationDefine
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class MovieType(BaseModel):
    name: str
    genre: str
    tmdbId: int


class MovieInfoType(BaseModel):
    movieInfo: List[MovieType]


class RatingType(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: str


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
    trainCollModel()
    return {"movieListIds": movieListIds}


@app.post("/setMovieRating")
async def setRating(userRating: RatingType = Body()):
    setNewUserRating(userRating)
    return {"message": 'Add Rating'}


@app.post("/getRecom")
async def getRecom(tmdbId, valueNumber=5):
    recom = recommendationDefine(int(tmdbId), int(valueNumber))
    return {"recommendation": recom}


@app.get("/content_recom")
async def content(movieId, valueNumber=5):
    recom = contentBasedRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}


@app.get("/coll_recom")
async def coll_recom(movieId, valueNumber=5):
    recom = collaborativeRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}
