import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_last_asin_by_reviewer_id(reviewer_id):
    with open('../database/reviews.json') as f:
        data = json.load(f)
        
    asin_list = []
    for record in data:
        if record['reviewerID'] == reviewer_id:
            asin_list.append(record['asin'])
    
    if asin_list:
        return asin_list[-1]
    else:
        return None

def get_product_name(asin):
    with open('../database/products.json') as f:
        products = json.load(f)
    for product in products:
        if product['asin'] == asin:
            return product['title']
    
    return None



def recommend_products(product_name, cosine):
    with open('../database/products.json') as f:
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
    with open('../database/products.json') as f:
        data = json.load(f)
        
    data = pd.DataFrame(data)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['tags'])
    cosine_sim = cosine_similarity(tfidf_matrix)
    
    recommendations = recommend_products(product_name, cosine_sim)
    return recommendations
