import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle

def trainModel():
    movies = pd.read_csv('movies.csv')
    ratings = pd.read_csv('ratings.csv')

    movies.drop(['genres'], axis = 1, inplace = True)
    movies.head(3)

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

def collRecom():
    movies = pd.read_csv('movies.csv')
    ratings = pd.read_csv('ratings.csv')

    movies.drop(['genres'], axis = 1, inplace = True)
    movies.head(3)

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
    recommendations = 5

    search_word = 'Fast and the Furious, The'
    movie_search = movies[movies['title'].str.contains(search_word)]
    movie_id = movie_search.iloc[0]['movieId']
    movie_id = user_item_matrix[user_item_matrix['movieId'] == movie_id].index[0]
    distances, indices = knn.kneighbors(csr_data[movie_id], n_neighbors = recommendations + 1)

    indices_list = indices.squeeze().tolist()
    distances_list = distances.squeeze().tolist()


    indices_distances = list(zip(indices_list, distances_list))

    print(type(indices_distances[0]))

    print(indices_distances[:3])

    indices_distances_sorted = sorted(indices_distances, key = lambda x: x[1], reverse = False)

    indices_distances_sorted = indices_distances_sorted[1:]

    recom_list = []

    for ind_dist in indices_distances_sorted:
        matrix_movie_id = user_item_matrix.iloc[ind_dist[0]]['movieId']
        id = movies[movies['movieId'] == matrix_movie_id].index
        title = movies.iloc[id]['title'].values[0]
        dist = ind_dist[1]
        recom_list.append({'Title' : title, 'Distance' : dist})

    recom_df = pd.DataFrame(recom_list, index = range(1, recommendations + 1))

    recom_df.to_csv('dataframe/recom_df.csv')