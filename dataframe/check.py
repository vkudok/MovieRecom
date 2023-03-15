import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle
import json

def trainModel():
    ratings = pd.read_csv('ratings.csv')

    # и ratings.csv (здесь также удаляем ненужный столбец timestamp)
    ratings.drop(['timestamp'], axis = 1, inplace = True)
    ratings.head(3)

    user_item_matrix = ratings.pivot(index = 'movieId', columns = 'userId', values= 'rating')
    user_item_matrix.head()

    user_item_matrix.fillna(0, inplace = True)
    user_item_matrix.head()

    users_votes = ratings.groupby('userId')['rating'].agg('count')

    movies_votes = ratings.groupby('movieId')['rating'].agg('count')

    user_mask = users_votes[users_votes > 50].index
    movie_mask = movies_votes[movies_votes > 10].index

    user_item_matrix = user_item_matrix.loc[movie_mask,:]

    user_item_matrix = user_item_matrix.loc[:,user_mask]

    csr_data = csr_matrix(user_item_matrix.values)

    print(csr_data[:2,:5])

    user_item_matrix = user_item_matrix.rename_axis(None, axis = 1).reset_index()
    user_item_matrix.head()

    knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute', n_neighbors = 20, n_jobs = -1)
    knn.fit(csr_data)

    # Its important to use binary mode
    knnPickle = open('dataframe/knnpickle_file', 'wb')

    # source, destination
    pickle.dump(knn, knnPickle)

    # close the file
    knnPickle.close()

def collRecom(findMovieId, numRecom):
    movies = pd.read_csv('movies2.csv', low_memory=False)
    ratings = pd.read_csv('ratings.csv', low_memory=False)

    # и ratings.csv (здесь также удаляем ненужный столбец timestamp)
    ratings.drop(['timestamp'], axis = 1, inplace = True)
    ratings.head(3)

    user_item_matrix = ratings.pivot(index = 'movieId', columns = 'userId', values= 'rating')
    user_item_matrix.head()

    user_item_matrix.fillna(0, inplace = True)
    user_item_matrix.head()

    users_votes = ratings.groupby('userId')['rating'].agg('count')

    movies_votes = ratings.groupby('movieId')['rating'].agg('count')

    user_mask = users_votes[users_votes > 50].index
    movie_mask = movies_votes[movies_votes > 10].index

    user_item_matrix = user_item_matrix.loc[movie_mask,:]

    user_item_matrix = user_item_matrix.loc[:,user_mask]

    csr_data = csr_matrix(user_item_matrix.values)

    print(csr_data[:2,:5])

    user_item_matrix = user_item_matrix.rename_axis(None, axis = 1).reset_index()
    user_item_matrix.head()

    knn = pickle.load(open('dataframe/knnpickle_file', 'rb'))

    recommendations = numRecom
    movie_id = findMovieId

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
        id = movies[movies['id'] == matrix_movie_id].index
        title = movies.iloc[id]['original_title']
        genres = movies.iloc[id]['genres']
        dist = ind_dist[1]
        recom_list.append({'Title' : title, 'Genres' : genres, 'Distance' : dist, 'id': movies['id']})

    recom_df = pd.DataFrame(recom_list, index = range(1, recommendations + 1))

    recom_df.to_csv('dataframe/recom_df.csv')

    return json.loads(recom_df.to_json(orient = "records"))