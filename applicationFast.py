from fastapi import FastAPI, Body, status
from trainModelRecom import addNewValuesInMovieAndLink, findMovieIdByTableId, trainModel, collRecom, setCsvInPSQL
import csv

class ResponseModel:
    def __init__(self, movie_title):
        self.movie_title = movie_title

app = FastAPI()

@app.get("/findMovieIdByTableId")
async def find():
    movies = {
        "movieInfo":
            [
                {
                    "name": "Toy Story (1995)",
                    "movieId": 862
                },
                {
                    "name": "Black Panther: Wakanda Forever",
                    "movieId": 505642
                },
                {
                    "name": "Knock at the Cabin",
                    "movieId": 631842
                }
            ]
    }
    listId = []
    for item in movies['movieInfo']:
        listId.append(item['movieId'])
    object = findMovieIdByTableId(listId)
    if(len(object['missingIds'])):
        addNewValuesInMovieAndLink(object['missingIds'], movies)
    else:
        find = 'not find'
    return {"message": object}

@app.get("/checkPSQL")
async def check():
    return {"message":'checkPSQL'}

@app.get("/addNewValuesInMovieAndLink")
async def trainNew():
    obeject = addNewValuesInMovieAndLink()
    return obeject

@app.get("/coll_recom")
async def coll_recom(movieId, valueNumber = 5):
    recom = collRecom(int(movieId), int(valueNumber))
    return {"recommendation": recom}

@app.get("/add_rating")
async def add_new():
    fields=["612","110","4.0","964982703"]
    with open(r'ratings.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    return {"message":'Add Rating'}