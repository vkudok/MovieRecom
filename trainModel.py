import pandas as pd
def recom():
    df_movies = pd.read_csv('movies.csv')
    df_ratings = pd.read_csv('ratings.csv')
    df_merged = pd.merge(df_movies, df_ratings, on='movieId', how='inner')
    df_merged.head()

    df = df_merged.pivot_table(index='userId', columns='title', values='rating')
    # Keep only movies that had at least 8 ratings
    df = df.dropna(thresh=8, axis=1)
    df.fillna(0, inplace=True)
    df.head()

    df_similarity = df.corr(method='pearson')
    #Store the data for later to be used in building the API
    df_similarity.to_csv('dataframe/movie_similarity.csv')
    df_similarity.head()
#
#
# from typing import Optional
# from flask import Flask, request
# from pydantic import BaseModel
# from flask_pydantic import validate  # Специальная пиздаболина для использования Pydantic
#
# app = Flask('flask_pydantic_app')
#
# class QueryModel(BaseModel):
#     age: int
#
# class ResponseModel(BaseModel):
#     id: int
#     age: int
#     name: str
#     nikname: Optional[str]
#
# @app.route("/", methods=["GET"])  # Pydantic схемы для автодокументирования не передаются
# @validate()  # pydantic модель передается не явно, а через декоратор
# def get(query: QueryModel):  # нет удобного depends и query как в FastAPI
#     age = query.age
# return ResponseModel(
#     age = age, id = 0, name = "abc", nikname = "123"
# )