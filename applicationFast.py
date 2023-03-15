from fastapi import FastAPI, Body, status
from trainModel import recom
from trainModelRecom import trainModel, collRecom
import csv

app = FastAPI()

@app.get("/train")
async def train():
    recom()
    return {"message":'train'}

@app.get("/trainNew")
async def trainNew():
    trainModel()
    return {"message":'trainModel'}

@app.get("/coll_recom")
async def coll_recom():
    recom = collRecom(2, 5)
    return {"recommendation": recom}

@app.get("/add_rating")
async def add_new():
    fields=["612","110","4.0","964982703"]
    with open(r'ratings.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    return {"message":'Add Rating'}
