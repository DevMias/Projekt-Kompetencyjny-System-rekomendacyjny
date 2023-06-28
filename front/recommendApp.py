import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from main import create_remote_db_connection
import subprocess


def import_users():
    remote_cnxn, remote_cursor = create_remote_db_connection()
    rows = remote_cursor.execute('select top 50 name, second_name, external_ref from Users').fetchall()
    remote_cursor.close()
    remote_cnxn.close()
    return rows


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

    def update_progress(self, dt):
        curr = self.ids.prg_bar.value
        curr += 0.25
        self.ids.prg_bar.value = curr
        self.ids.prg_lab.text = f"{int(curr * 100)}% progress"

        if curr < 1.0:
            Clock.schedule_once(self.update_progress, 1)
        else:
            app = App.get_running_app()
            app.root.current = "recommended"

    def run_script(self, script, args):
        try:
            result = subprocess.run(["python", str(script), str(args)], capture_output=True, text=True)
            self.result = result.stdout.strip()  # Save the result
            return result
        except subprocess.CalledProcessError as e:
            error_output = e.output.strip()
            print(f"Script execution error: {error_output}")
            return None

    def start_recommendation_thread(self):
        if ChooseRecommendationMethod.recommendation_option == 0:
            script = '../backend/similarity_recomendation.py'
            args = str(ChoosePerson.external_ref)
        elif ChooseRecommendationMethod.recommendation_option == 1:
            script = '../backend/reviews_recomendation.py'
            args = str(ChoosePerson.external_ref)
        else:
            return None

        self.update_progress(0)  # Start the progress bar
        self.run_script(script, args)  # Execute the script and save the result

        result = self.result  # Retrieve the result from the class attribute

        return result


class RecommendedProducts(Screen):
    recommendations = [LoadingScreen.result]

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
        font_size = int(screen_width / 30)

        for recommendation in RecommendedProducts.recommendations:
            label = Label(text=recommendation, font_size=font_size, color=(0, 0, 0, 1))
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
