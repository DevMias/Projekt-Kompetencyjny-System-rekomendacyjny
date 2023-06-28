import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

def get_similarity_recommendations_by_reviewer_id(reviewer_id):
    with open('../database/reviews.json') as f:
        reviews_data = json.load(f)
    with open('../database/products.json') as f:
        products_data = json.load(f)

    reviews = pd.DataFrame(reviews_data)
    products = pd.DataFrame(products_data)

    user_reviews = reviews[reviews['reviewerID'] == reviewer_id]
    if user_reviews.empty:
        return None

    user_last_asin = user_reviews['asin'].iloc[-1]
    product_name = products[products['asin'] == user_last_asin]['title'].iloc[0]

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(products['tags'])
    cosine_sim = cosine_similarity(tfidf_matrix)

    product_index = products[products['title'] == product_name].index[0]
    dist = list(enumerate(cosine_sim[product_index]))
    dist.sort(reverse=True, key=lambda x: x[1])
    recommendations = []
    for i in dist[1:5]:
        similar_product = products.iloc[i[0]]['title']
        similarity_value = i[1]
        recommendations.append((similar_product, similarity_value))
    return recommendations

# Example usage
#reviewer_id = 'A1727O77XSE5QQ'
#recommendations = get_recommendations_by_reviewer_id(reviewer_id)

#if recommendations:
#    print(f"Recommended products for reviewer ID '{reviewer_id}':")
#    for product, score in recommendations:
#        print(f"Product: {product}, Score: {score}")
#else:
#    print(f"No recommendations found for reviewer ID '{reviewer_id}'.")
