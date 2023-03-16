from fastapi import FastAPI, Body, status
from trainModelRecom import trainModel, collRecom, setCsvInPSQL
import csv

class ResponseModel:
    def __init__(self, movie_title):
        self.movie_title = movie_title

app = FastAPI()

@app.get("/checkPSQL")
async def check():
    setCsvInPSQL()
    return {"message":'checkPSQL'}

@app.get("/trainNew")
async def trainNew():
    trainModel()
    return {"message":'trainModel'}

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