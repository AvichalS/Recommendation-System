# -*- coding: utf-8 -*-
"""Recommender system.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j_LIhonG4Lu3dKVZktsDBOxzSYbWTGjA

Importing dependencies
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive
drive.mount('/content/gdrive')

"""Load data"""

ratings=pd.read_csv("/content/gdrive/MyDrive/Recommender system/ratings.csv")
movies=pd.read_csv("/content/gdrive/MyDrive/Recommender system/movies.csv")

"""Exploratory analysis"""

n_ratings = len(ratings)
n_movies = ratings['movieId'].nunique()
n_users = ratings['userId'].nunique()

print(f"Number of ratings: {n_ratings}")
print(f"Number of unique movieId's: {n_movies}")
print(f"Number of unique users: {n_users}")
print(f"Average number of ratings per user: {round(n_ratings/n_users, 2)}")
print(f"Average number of ratings per movie: {round(n_ratings/n_movies, 2)}")

sns.countplot(x="rating", data=ratings, palette="viridis")
plt.title("Distribution of movie ratings", fontsize=14)
plt.show()

print(f"Mean global rating: {round(ratings['rating'].mean(),2)}.")

mean_ratings = ratings.groupby('userId')['rating'].mean()
print(f"Mean rating per user: {round(mean_ratings.mean(),2)}.")

"""Best & Worst movie"""

mean_ratings = ratings.groupby('movieId')[['rating']].mean()
lowest_rated = mean_ratings['rating'].idxmin()
movies[movies['movieId'] == lowest_rated]

highest_rated = mean_ratings['rating'].idxmax()
movies[movies['movieId'] == highest_rated]

"""Bayesian Average"""

movie_stats = ratings.groupby('movieId')[['rating']].agg(['count', 'mean'])
movie_stats.columns = movie_stats.columns.droplevel()

C = movie_stats['count'].mean()
m = movie_stats['mean'].mean()

def bayesian_avg(ratings):
    bayesian_avg = (C*m+ratings.sum())/(C+ratings.count())
    return bayesian_avg

bayesian_avg_ratings = ratings.groupby('movieId')['rating'].agg(bayesian_avg).reset_index()
bayesian_avg_ratings.columns = ['movieId', 'bayesian_avg']
movie_stats = movie_stats.merge(bayesian_avg_ratings, on='movieId')

movie_stats.sort_values('bayesian_avg', ascending=True).head()

"""Genre Analysis"""

movies['genres'] = movies['genres'].apply(lambda x: x.split("|"))
movies.head()

from collections import Counter
genre_frequency = Counter(g for genres in movies['genres'] for g in genres)
print(f"There are {len(genre_frequency)} genres.")
genre_frequency

print("The 5 most common genres: \n", genre_frequency.most_common(5))

"""Data Pre-processing"""

from scipy.sparse import csr_matrix
def create_X(df):
    """
    Generates a sparse matrix from ratings dataframe.
    Args:
        df: pandas dataframe containing 3 columns (userId, movieId, rating)
    Returns:
        X: sparse matrix
        user_mapper: dict that maps user id's to user indices
        user_inv_mapper: dict that maps user indices to user id's
        movie_mapper: dict that maps movie id's to movie indices
        movie_inv_mapper: dict that maps movie indices to movie id's
    """
    M = df['userId'].nunique()
    N = df['movieId'].nunique()
    user_mapper = dict(zip(np.unique(df["userId"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movieId"]), list(range(N))))
    user_inv_mapper = dict(zip(list(range(M)), np.unique(df["userId"])))
    movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movieId"])))
    user_index = [user_mapper[i] for i in df['userId']]
    item_index = [movie_mapper[i] for i in df['movieId']]
    X = csr_matrix((df["rating"], (user_index,item_index)), shape=(M,N))
    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper
X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(ratings)

"""Evaluating sparsity"""

n_total = X.shape[0]*X.shape[1]
n_ratings = X.nnz
sparsity = n_ratings/n_total
print(f"Matrix sparsity: {round(sparsity*100,2)}%")

"""Cold Start problem"""

n_ratings_per_user = X.getnnz(axis=1)

print(f"Most active user rated {n_ratings_per_user.max()} movies.")
print(f"Least active user rated {n_ratings_per_user.min()} movies.")

n_ratings_per_movie = X.getnnz(axis=0)

print(f"Most rated movie has {n_ratings_per_movie.max()} ratings.")
print(f"Least rated movie has {n_ratings_per_movie.min()} ratings.")

plt.figure(figsize=(16,4))
plt.subplot(1,2,1)
sns.kdeplot(n_ratings_per_user, shade=True)
plt.xlim(0)
plt.title("Number of Ratings Per User", fontsize=14)
plt.xlabel("number of ratings per user")
plt.ylabel("density")
plt.subplot(1,2,2)
sns.kdeplot(n_ratings_per_movie, shade=True)
plt.xlim(0)
plt.title("Number of Ratings Per Movie", fontsize=14)
plt.xlabel("number of ratings per movie")
plt.ylabel("density")
plt.show()

"""Normalising data"""

sum_ratings_per_movie = X.sum(axis=0)
mean_rating_per_movie = sum_ratings_per_movie/n_ratings_per_movie

X_mean_movie = np.tile(mean_rating_per_movie, (X.shape[0],1))
X_mean_movie.shape

X_norm = X - csr_matrix(X_mean_movie)

print("Original X:", X[0].todense())
print("Normalized X:", X_norm[0].todense())

"""Item-Item Recommendations"""

from sklearn.neighbors import NearestNeighbors
def find_similar_movies(movie_id, X, movie_mapper, movie_inv_mapper, k, metric='cosine'):
    """
    Finds k-nearest neighbours for a given movie id.
    Args:
        movie_id: id of the movie of interest
        X: user-item utility matrix
        k: number of similar movies to retrieve
        metric: distance metric for kNN calculations
    Output: returns list of k similar movie ID's
    """
    X = X.T
    neighbour_ids = []
    movie_ind = movie_mapper[movie_id]
    movie_vec = X[movie_ind]
    if isinstance(movie_vec, (np.ndarray)):
        movie_vec = movie_vec.reshape(1,-1)
    # use k+1 since kNN output includes the movieId of interest
    kNN = NearestNeighbors(n_neighbors=k+1, algorithm="brute", metric=metric)
    kNN.fit(X)
    neighbour = kNN.kneighbors(movie_vec, return_distance=False)
    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(movie_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids

similar_movies = find_similar_movies(1, X_norm, movie_mapper, movie_inv_mapper, k=10)
similar_movies

"""Implementing using Cosine Metric"""

movie_titles = dict(zip(movies['movieId'], movies['title']))
movie_id = 1
similar_movies = find_similar_movies(movie_id, X_norm, movie_mapper, movie_inv_mapper, metric='cosine', k=10)
movie_title = movie_titles[movie_id]
print(f"Because you watched {movie_title}:")
for i in similar_movies:
    print(movie_titles[i])

"""Implementing using Euclidean Metric"""

movie_id = 1
similar_movies = find_similar_movies(movie_id, X_norm, movie_mapper, movie_inv_mapper, metric='euclidean', k=10)
movie_title = movie_titles[movie_id]
print(f"Because you watched {movie_title}:")
for i in similar_movies:
    print(movie_titles[i])

"""Handling cold start"""

n_movies = movies['movieId'].nunique()
print(f"There are {n_movies} unique movies in our movies dataset.")

genres = set(g for G in movies['genres'] for g in G)
for g in genres:
    movies[g] = movies.genres.transform(lambda x: int(g in x))
movie_genres = movies.drop(columns=['movieId', 'title','genres'])
movie_genres.head()

from sklearn.metrics.pairwise import cosine_similarity
cosine_sim = cosine_similarity(movie_genres, movie_genres)
print(f"Dimensions of our genres cosine similarity matrix: {cosine_sim.shape}")

def movie_finder(title):
    return movies[movies['title'].str.contains(title)]['title'].tolist()
movie_finder('Toy Story')

movie_idx = dict(zip(movies['title'], list(movies.index)))
title = movie_finder('Toy Story')[0]
n_recommendations = 10
idx = movie_idx[title]
sim_scores = list(enumerate(cosine_sim[idx]))
sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
sim_scores = sim_scores[1:(n_recommendations+1)]
similar_movies = [i[0] for i in sim_scores]

print(f"Recommendations for {title}:")
movies['title'].iloc[similar_movies]

"""Matrix Factorisation"""

from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=20, n_iter=10)
Z = svd.fit_transform(X.T)

movie_id = 1
similar_movies = find_similar_movies(movie_id, Z.T, movie_mapper, movie_inv_mapper, metric='cosine', k=10)
movie_title = movie_titles[movie_id]

print(f"Because you watched {movie_title}:")
for i in similar_movies:
    print(movie_titles[i])

"""Predicting missing ratings"""

new_X = svd.inverse_transform(Z).T

userId = 99
user_preferences = ratings[(ratings['userId']==userId)&(ratings['rating']>=4)]
user_preferences = user_preferences.merge(movies[['movieId', 'title']])
user_preferences.sort_values('rating', ascending=False).head(10)

top_N = 10
movie_titles = dict(zip(movies['movieId'], movies['title']))
top_N_indices = new_X[user_mapper[userId]].argsort()[-top_N:][::-1]
print(f"Top {top_N} Recommendations for UserId {userId}:")
for i in top_N_indices:
    movie_id = movie_inv_mapper[i]
    print(movie_titles[movie_id])