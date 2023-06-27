import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_products(product_name, cosine):
    with open('products.json') as f:
        data = json.load(f)
        
    data = pd.DataFrame(data)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['tags'])
    cosine_sim = cosine_similarity(tfidf_matrix)

    index = data[data['title'] == product_name].index[0]
    dist = list(enumerate(cosine[index]))
    dist.sort(reverse=True, key=lambda x: x[1])
    recommendations = []
    for i in dist[1:5]:
        similar_product = data.iloc[i[0]]['title']
        similarity_value = i[1]
        recommendations.append((similar_product, similarity_value))
    return recommendations

def get_recommendations(product_name):
    with open('products.json') as f:
        data = json.load(f)
        
    data = pd.DataFrame(data)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['tags'])
    cosine_sim = cosine_similarity(tfidf_matrix)
    
    recommendations = recommend_products(product_name, cosine_sim)
    return recommendations
