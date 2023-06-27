import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open('products.json') as f:
    data = json.load(f)
        
data = pd.DataFrame(data)


tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['tags'])
cosine_sim = cosine_similarity(tfidf_matrix)

def recommend_products(title,cosine):
    index = data[data['title'] == title].index[0]
    dist = list(enumerate(cosine[index]))
    dist.sort(reverse=True, key=lambda x: x[1])
    for i in dist[1:5]:
        similarity_value = i[1]
        print(data.iloc[i[0]]['title'], similarity_value)

def get(cosine):
    product = input("Enter product name: ")
    print(f"\nRecommended products after buying {product}: ")
    recommend_products(product,cosine)
    
get(cosine_sim)
