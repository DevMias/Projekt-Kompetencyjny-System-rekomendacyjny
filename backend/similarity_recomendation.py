import ast
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = []
i = 0
with open('output.json', 'r') as file:
    for line in file:
        if i > 20000:
            break
        item = ast.literal_eval(line)
        data.append(item)
        i += 1
        
data = pd.DataFrame(data)
data = data[['asin','categories','title','description','price','brand']]
data.head()
data = data.dropna(subset=['categories'])
data = data.dropna(subset=['title'])
data['categories'] = data['categories'].apply(lambda x: ', '.join([', '.join(sublist) for sublist in x]))
data.head()
#wartosci NaN na pusty tekst
data[['description', 'price', 'brand']] = data[['description', 'price', 'brand']].fillna('')
#zmiana typu na tekst
data[['categories','description','price','brand']] = data[['categories','description','price','brand']].astype(str)
#polaczenie kolumn w tag
data['tags'] = data[['categories','description','price','brand']].apply(lambda row: " ".join(row), axis=1)

data = data.drop(columns = ['categories','description','price','brand'])

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['tags'])
cosine_sim = cosine_similarity(tfidf_matrix)

def recommend_products(title,cosine):
    index = data[data['title'] == title].index[0]
    dist = list(enumerate(cosine[index]))
    dist.sort(reverse=True, key=lambda x: x[1])
    for i in dist[1:15]:
        similarity_value = i[1]
        print(data.iloc[i[0]]['title'], similarity_value)

def get(cosine):
    product = input("Enter product name: ")
    print(f"\nRecommended products after buying {product}: ")
    recommend_products(product,cosine)
    
get(cosine_sim)