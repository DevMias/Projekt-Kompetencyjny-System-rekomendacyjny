import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import operator
import random

with open('reviews.json') as f:
    data = json.load(f)

reviews = pd.DataFrame(data)
reviews.head()

tab = reviews.pivot_table(index='reviewerID', columns='asin', values='overall')
tab = tab.fillna(0)

similarity_matrix = cosine_similarity(tab.values)

def recommend_items(user_id, top_n=5):
    user_index = tab.index.get_loc(user_id)
    user_similarities = similarity_matrix[user_index]
    
    top_similar_users = user_similarities.argsort()[::-1][1:top_n+1]
    
    item_recommendations = {}
    
    for similar_user_index in top_similar_users:
        similar_user_id = tab.index[similar_user_index]
        
        items_rated_by_similar_user = tab.iloc[similar_user_index]
        

        for item_id, rating in items_rated_by_similar_user.items():
            if tab.iloc[user_index][item_id] == 0.0 and rating > 0.0:
                if item_id not in item_recommendations:
                    item_recommendations[item_id] = rating
                else:
                    item_recommendations[item_id] += rating
    
    sorted_recommendations = sorted(item_recommendations.items(), key=lambda x: x[1], reverse=True)
    return sorted_recommendations[:top_n]

unique_users = reviews['reviewerID'].unique()
random.shuffle(unique_users)
users = unique_users[:50]
scores = []

for user_id in users:
    recommendations = recommend_items(user_id, top_n=5)

    for item_id, score in recommendations:
        scores.append(score)
print("Mean Score:", np.mean(scores))
