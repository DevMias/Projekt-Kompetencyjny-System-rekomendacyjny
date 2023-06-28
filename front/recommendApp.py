from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from main import create_remote_db_connection
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import numpy as np
import random


def import_users():
    remote_cnxn, remote_cursor = create_remote_db_connection()
    rows = remote_cursor.execute('select top 50 name, second_name, external_ref from Users').fetchall()
    remote_cursor.close()
    remote_cnxn.close()
    return rows


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


def recommend_products(user_id):
    with open('../database/reviews.json') as f:
        data = json.load(f)

    with open('../database/products.json') as f_meta:
        meta = json.load(f_meta)

    metadata = pd.DataFrame(meta)

    reviews = pd.DataFrame(data)

    tab = reviews.pivot_table(index='reviewerID', columns='asin', values='overall')
    tab = tab.fillna(0)

    similarity_matrix = cosine_similarity(tab.values)

    def recommend_items(user_id, top_n=5):
        user_index = tab.index.get_loc(user_id)
        user_similarities = similarity_matrix[user_index]

        top_similar_users = user_similarities.argsort()[::-1][1:top_n + 1]

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

    file_name = 'mean_reviews_recom_score.txt'

    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            mean_value = file.read()
            print("Zawartość pliku:", mean_value)
    else:
        scores = []
        for user_id in users:
            recommendations = recommend_items(user_id, top_n=5)
            for item_id, score in recommendations:
                scores.append(score)
        mean_score = np.mean(scores)

        with open(file_name, "w") as file:
            file.write(str(mean_score))

    recommendations = recommend_items(user_id, top_n=5)
    results = []
    for item_id, score in recommendations:
        product_name = metadata.loc[metadata['asin'] == item_id, 'title'].values[0]
        results.append((product_name, score))
    return results


class WindowManager(ScreenManager):
    pass


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
    external_ref = 0

    def on_enter(self):
        self.clear_carousel()
        self.setup_carousel()

    def setup_carousel(self):
        names = import_users()

        carousel = Carousel(direction='right')
        carousel.clear_widgets()

        screen_width = Window.width
        font_size = int(screen_width / 30)

        for name in names:
            label = Label(text=name[0] + ' ' + name[1], font_size=font_size, color=(0, 0, 0, 1))
            carousel.add_widget(label)

        self.ids.carousel_container.add_widget(carousel)

    def clear_carousel(self):
        self.ids.carousel_container.clear_widgets()

    def show_previous(self):
        carousel = self.ids.carousel_container.children[0]
        carousel.load_previous()

    def show_next(self):
        carousel = self.ids.carousel_container.children[0]
        carousel.load_next()

    def submit(self):
        carousel = self.ids.carousel_container.children[0]
        current_index = carousel.index

        names = import_users()
        external_ref = names[current_index][2]

        ChoosePerson.external_ref = external_ref

        app = App.get_running_app()
        app.root.current = "recommend"

        return ChoosePerson.external_ref


class ChooseRecommendationMethod(Screen):
    recommendation_option = 0
    result = None

    def submit_people_method(self):
        ChooseRecommendationMethod.recommendation_option = 1

        app = App.get_running_app()
        app.root.current = "load"

        return ChooseRecommendationMethod.recommendation_option

    def submit_products_method(self):
        ChooseRecommendationMethod.recommendation_option = 0

        app = App.get_running_app()
        app.root.current = "load"

        return ChooseRecommendationMethod.recommendation_option


class LoadingScreen(Screen):
    result = None

    def on_pre_enter(self):
        self.ids.prg_bar.value = 0
        self.ids.prg_lab.text = "0% progress"

    def on_enter(self):
        self.update_progress(self)

    def update_progress(self, dt):
        curr = self.ids.prg_bar.value
        curr += 0.05
        self.ids.prg_bar.value = curr
        self.ids.prg_lab.text = f"{int(curr * 100)}% progress"

        if curr < 1.0:
            Clock.schedule_once(self.update_progress, 1)
        else:
            app = App.get_running_app()
            app.root.current = "recommended"

    def start_recommendation_thread(self):
        if ChooseRecommendationMethod.recommendation_option == 0:
            LoadingScreen.result = get_similarity_recommendations_by_reviewer_id(ChoosePerson.external_ref)
        elif ChooseRecommendationMethod.recommendation_option == 1:
            LoadingScreen.result = recommend_products(ChoosePerson.external_ref)
        else:
            return None

        self.update_progress(0)  # Start the progress bar

        return LoadingScreen.result


class RecommendedProducts(Screen):

    def switch_to_first_screen(self):
        screen_manager = self.manager
        screen_manager.current = 'welcome'

    def on_enter(self):
        self.clear_carousel()
        self.setup_carousel()

    def setup_carousel(self):
        carousel = Carousel(direction='right')
        carousel.clear_widgets()

        screen_width = Window.width
        font_size = int(screen_width / 60)

        for rec, acc in LoadingScreen.result:
            label = Label(text=rec+"\n"+str(round(acc, 5)), font_size=font_size, color=(0, 0, 0, 1))
            carousel.add_widget(label)

        self.ids.carousel_container2.add_widget(carousel)

    def clear_carousel(self):
        self.ids.carousel_container2.clear_widgets()

    def show_previous(self):
        carousel = self.ids.carousel_container2.children[0]
        carousel.load_previous()

    def show_next(self):
        carousel = self.ids.carousel_container2.children[0]
        carousel.load_next()


class RecommendApp(App):
    def build(self):
        return WindowManager()


if __name__ == '__main__':
    RecommendApp().run()
