import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle
import json
from sqlalchemy import create_engine

POSTGRESQL_HOSTS = 'postgresql://postgres:1234@localhost:5432/movieinfo'

def trainModel():
    engine = create_engine(POSTGRESQL_HOSTS)
    ratings = pd.read_sql_table('ratings', engine)

    ratings.drop(['timestamp'], axis = 1, inplace = True)

    user_item_matrix = ratings.pivot(index = 'movieId', columns = 'userId', values= 'rating')
    user_item_matrix.fillna(0, inplace = True)

    users_votes = ratings.groupby('userId')['rating'].agg('count')
    movies_votes = ratings.groupby('movieId')['rating'].agg('count')

    user_item_matrixPickle = open('dataframe/user_item_matrix', 'wb')
    pickle.dump(user_item_matrix, user_item_matrixPickle)
    user_item_matrixPickle.close()

    user_mask = users_votes[users_votes > 50].index
    movie_mask = movies_votes[movies_votes > 10].index

    user_item_matrix = user_item_matrix.loc[movie_mask,:]

    user_item_matrix = user_item_matrix.loc[:,user_mask]

    csr_data = csr_matrix(user_item_matrix.values)

    csr_dataPickle = open('dataframe/csr_data', 'wb')
    pickle.dump(csr_data, csr_dataPickle)
    csr_dataPickle.close()

    user_item_matrix = user_item_matrix.rename_axis(None, axis = 1).reset_index()

    user_item_matrixPickle = open('dataframe/user_item_matrix', 'wb')
    pickle.dump(user_item_matrix, user_item_matrixPickle)
    user_item_matrixPickle.close()

    knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute', n_neighbors = 20, n_jobs = -1)
    knn.fit(csr_data)

    knnPickle = open('dataframe/knnpickle_file', 'wb')

    pickle.dump(knn, knnPickle)

    knnPickle.close()

def setCsvInPSQL():
    columns = [
        "userId",
        "movieId",
        "rating",
        "timestamp"
    ]

    df = pd.read_csv(
        "ratings.csv",
        names=columns
    )

    engine = create_engine(POSTGRESQL_HOSTS)

    df.to_sql(
        'ratings',
        engine,
        index=False
    )

def collRecom(id, numRecom):
    engine = create_engine(POSTGRESQL_HOSTS)
    movies = pd.read_sql_table('movies', engine)
    links = pd.read_sql_table('links', engine)
    knn = pickle.load(open('dataframe/knnpickle_file', 'rb'))
    user_item_matrix = pickle.load(open('dataframe/user_item_matrix', 'rb'))
    csr_data = pickle.load(open('dataframe/csr_data', 'rb'))

    recommendations = numRecom
    movie_id = id

    movie_id = user_item_matrix[user_item_matrix['movieId'] == movie_id].index[0]
    distances, indices = knn.kneighbors(csr_data[movie_id], n_neighbors = recommendations + 1)

    indices_list = indices.squeeze().tolist()
    distances_list = distances.squeeze().tolist()

    indices_distances = list(zip(indices_list, distances_list))

    indices_distances_sorted = sorted(indices_distances, key = lambda x: x[1], reverse = False)

    indices_distances_sorted = indices_distances_sorted[1:]

    recom_list = []

    for ind_dist in indices_distances_sorted:
        matrix_movie_id = user_item_matrix.iloc[ind_dist[0]]['movieId']
        id = movies[movies['movieId'] == matrix_movie_id].index
        title = movies.iloc[id]['title'].values[0]
        movie_id = movies.iloc[id]['movieId'].values[0]
        tmdbId = links.iloc[id]['tmdbId'].values[0]
        dist = ind_dist[1]
        recom_list.append({'title' : title, 'movie_id' : movie_id, 'tmdbId': tmdbId, 'distance' : dist})

    recom_df = pd.DataFrame(recom_list, index = range(1, recommendations + 1))

    return json.loads(recom_df.to_json(orient = "records"))