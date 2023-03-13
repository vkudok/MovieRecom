from flask import Flask, jsonify, request, make_response, json
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
best_friends = {'Monica':'Rachel','Joey':'Chandler','Ross':'Phoebe'}

@app.route("/")
def hello_from_root():
    recom()
    return jsonify(message='Hello from root!')

@app.route("/train")
def train_rec():
    recom()
    return jsonify(message='Train')

# @app.route("/recms", methods = ["POST"])
# def make_rec():
#     if request.method == "POST":
#         data = json.loads(request.data)
#         movie = data["movie_title"]
#         item_similarity_df = pd.read_csv("dataframe/movie_similarity.csv", index_col=0)
#         # curl.exe -X POST -H "Content-type: text/plain" -d "{"movie_title":"Heat (1995)"}" "http://10.8.0.12:8000/recms"
#         try:
#             similar_score = item_similarity_df[movie]
#             similar_movies = similar_score.sort_values(ascending=False)[1:50]
#             api_recommendations = similar_movies.index.to_list()
#         except:
#             api_recommendations = ['Movie not found']
#         return ResponseModel(rec_movie = api_recommendations)


@app.route("/find_friend", methods=['POST','GET'])
def get_best_friend(data):
    # person = request.json["person"]
    #curl -X POST http://0.0.0.0:80/find_friend -H 'Content-Type: application/json' -d '{"person":"Joey"}'
    return jsonify(data)

if __name__ == "__main__":
    appPort = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='10.8.0.12', port=appPort)

