import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import fuzz
import pandas as pd
from sqlalchemy import create_engine

POSTGRESQL_HOSTS = 'postgresql://postgres:1234@localhost:5432/movieinfo'

engine = create_engine(POSTGRESQL_HOSTS)


# the function to extract titles
def extract_title(title):
    year = title[len(title) - 5:len(title) - 1]
    # some movies do not have the info about year in the column title. So, we should take care of the case as well.
    if year.isnumeric():
        title_no_year = title[:len(title) - 7]
        return title_no_year
    else:
        return title


# the function to extract years
def extract_year(title):
    year = title[len(title) - 5:len(title) - 1]
    # some movies do not have the info about year in the column title. So, we should take care of the case as well.
    if year.isnumeric():
        return int(year)
    else:
        return np.nan


def prepareData():
    # change the column name from title to title_year
    movies = pd.read_csv('movie.csv')
    movies.rename(columns={'title': 'title_year'}, inplace=True)
    # remove leading and ending whitespaces in title_year
    movies['title_year'] = movies['title_year'].apply(lambda x: x.strip())
    # create the columns for title and year
    movies['title'] = movies['title_year'].apply(extract_title)
    movies['year'] = movies['title_year'].apply(extract_year)
    # remove the movies without genre information and reset the index
    movies = movies[~(movies['genres'] == '(no genres listed)')].reset_index(drop=True)

    # remove '|' in the genres column
    movies['genres'] = movies['genres'].str.replace('|', ' ')

    # change 'Sci-Fi' to 'SciFi' and 'Film-Noir' to 'Noir'
    movies['genres'] = movies['genres'].str.replace('Sci-Fi', 'SciFi')
    movies['genres'] = movies['genres'].str.replace('Film-Noir', 'Noir')

    return movies


def tfidfVector():
    movies = prepareData()
    # create an object for TfidfVectorizer
    tfidf_vector = TfidfVectorizer(stop_words='english')
    # apply the object to the genres column
    tfidf_matrix = tfidf_vector.fit_transform(movies['genres'])
    tfidf_matrix.shape

    # create the cosine similarity matrix
    sim_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)
    recomenderMovies = contents_based_recommender('Monsters, Inc.', 5, movies, sim_matrix)

    return recomenderMovies


# a function to convert index to title_year
def get_title_year_from_index(index, movies):
    return movies[movies.index == index]['title_year'].values[0]


# # a function to convert index to title
# def get_title_from_index(index, movies):
#     return movies[movies.index == index]['title'].values[0]


# a function to convert title to index
def get_index_from_title(title, movies):
    return movies[movies.title == title].index.values[0]


def contents_based_recommender(movie_user_likes, how_many, movies, sim_matrix):
    recommenderMovies = []
    movie_index = get_index_from_title(movie_user_likes, movies)
    movie_list = list(enumerate(sim_matrix[int(movie_index)]))
    # remove the typed movie itself
    similar_movies = list(
        filter(lambda x: x[0] != int(movie_index), sorted(movie_list, key=lambda x: x[1], reverse=True)))

    for i, s in similar_movies[:how_many]:
        recommenderMovies.append(get_title_year_from_index(i, movies))

    return recommenderMovies
