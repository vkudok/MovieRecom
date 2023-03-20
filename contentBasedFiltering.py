import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import json
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
    movies = pd.read_sql_table('movies', engine)

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


def contentBasedRecom(id, numRecom):
    movies = prepareData()
    # create an object for TfidfVectorizer
    tfidf_vector = TfidfVectorizer(stop_words='english')
    # apply the object to the genres column
    tfidf_matrix = tfidf_vector.fit_transform(movies['genres'])

    # create the cosine similarity matrix
    sim_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)
    recomenderMovies = recommender(id, numRecom, movies, sim_matrix)
    return recomenderMovies


# a function to convert index to title_year
def get_title_year_from_index(index, movies):
    return movies[movies.index == index]['title_year'].values[0]


# a function to convert index to title_year
def get_movieId_from_index(index, movies):
    return movies[movies.index == index]['movieId'].values[0]


def recommender(entryMovieId, how_many, movies, sim_matrix):
    links = pd.read_sql_table('links', engine)

    strIndex = movies[movies.movieId == entryMovieId].index.values[0]

    recommenderMovies = []
    movie_list = list(enumerate(sim_matrix[int(strIndex)]))
    # remove the typed movie itself
    similar_movies = list(
        filter(lambda x: x[0] != int(entryMovieId), sorted(movie_list, key=lambda x: x[1], reverse=True)))

    for id, s in similar_movies[:how_many]:
        movie_id = get_movieId_from_index(id, movies)
        title = get_title_year_from_index(id, movies)
        linkId = links[links['movieid'] == movie_id].index
        tmdbId = links.iloc[linkId]['tmdbid'].values[0]
        recommenderMovies.append({'title': title, 'movie_id': movie_id, 'tmdbId': tmdbId, 'cotent': 'cotent'})

    recom_df = pd.DataFrame(recommenderMovies)

    return json.loads(recom_df.to_json(orient="records"))
