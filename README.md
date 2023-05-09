# Recommendation-System
Developed a movie recommendation system using k-means clustering given a set of movies and ratings csv files. Other concepts used: baysian statistics, matrix factorization, collaborative filtering.

The first part of the code loads and performs an exploratory analysis of the data. 
The second part pre-processes the data for modelling by creating a sparse matrix and performing a train-test split.
The third part of the code implements a model to make movie recommendations based on user input. The model calculates the cosine similarity between movies and returns the top-k most similar movies as recommendations.
