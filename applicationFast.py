from fastapi import FastAPI, Body, status
from trainModel import recom
from trainModelRecom import trainModel, collRecom
import pandas as pd
import csv

class ResponseModel:
    def __init__(self, movie_title):
        self.movie_title = movie_title

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
    collRecom()
    return {"message":'coll_recom'}

@app.get("/add_rating")
async def add_new():
    fields=["612","110","4.0","964982703"]
    with open(r'ratings.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    return {"message":'Add Rating'}

@app.post("/recommendation")
def get_recommendation(data  = Body()):
    movie = ResponseModel(data["movie_title"])
    item_similarity_df = pd.read_csv("dataframe/movie_similarity.csv", index_col=0)
    try:
        similar_score = item_similarity_df[movie.movie_title]
        similar_movies = similar_score.sort_values(ascending=False)[1:50]
        api_recommendations = similar_movies.index.to_list()
    except:
        api_recommendations = ['Movie not found']
    return {"rec_movie" : api_recommendations}
