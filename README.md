# Recommendation-System
This code implements a recommendation system using collaborative filtering. It begins by importing necessary libraries and loading movie rating data. Exploratory analysis is performed on the data to determine the number of ratings, unique users, and movies, as well as the distribution of movie ratings. The Bayesian average method is used to address the "cold start" problem and make more accurate movie recommendations. The code also includes genre analysis and data pre-processing to generate a sparse matrix from the rating data. The sparsity of the matrix is evaluated, and normalization is performed before the final recommendation model is built.

1. The first part of the code loads and performs an exploratory analysis of the data. 
2. The second part pre-processes the data for modelling by creating a sparse matrix and performing a train-test split.
3. The third part of the code implements a model to make movie recommendations based on user input. The model calculates the cosine similarity between movies and returns the top-k most similar movies as recommendations.
