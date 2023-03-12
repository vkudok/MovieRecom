from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import pandas as pd
import os
from trainModel import recom
from typing import List
from pydantic import BaseModel
from flask_pydantic import validate
from os import path

app = Flask(__name__)
CORS(app, supports_credentials=True)

class ResponseModel(BaseModel):
    rec_movie: List

@app.route("/")
def hello_from_root():
    recom()
    return jsonify(message='Hello from root!')

@app.route("/train")
def train_rec():
    recom()
    return jsonify(message='Train')

@app.route("/recms", methods = ["POST"])
@validate()
def make_rec():
    if request.method == "POST":
        data = request.json
        movie = data["movie_title"]
        item_similarity_df = pd.read_csv("dataframe/movie_similarity.csv", index_col=0)
        # curl -X POST http://10.8.0.12:8000/recms -H 'Content-Type: application/json' -d '{"movie_title":"Heat (1995)"}'
        try:
            similar_score = item_similarity_df[movie]
            similar_movies = similar_score.sort_values(ascending=False)[1:50]
            api_recommendations = similar_movies.index.to_list()
        except:
            api_recommendations = ['Movie not found']
        return ResponseModel(rec_movie = api_recommendations)

if __name__ == "__main__":
    appPort = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='10.8.0.12', port=appPort)

