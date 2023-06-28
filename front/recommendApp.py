from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from main import create_remote_db_connection
from backend import reviews_recomendation as rev
from backend import similarity_recomendation as sim


def importUsers():
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
    def on_enter(self):
        self.clear_carousel()
        self.setup_carousel()

    def setup_carousel(self):
        names = importUsers()

        carousel = Carousel(direction='right')
        carousel.clear_widgets()

        screen_width = Window.width
        font_size = int(screen_width / 30)

        for name in names:
            label = Label(text=name[0]+' '+name[1], font_size=font_size, color=(0, 0, 0, 1))
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


class ChooseRecommendationMethod(Screen):
    pass


class LoadingScreen(Screen):
    def on_pre_enter(self):
        self.ids.prg_bar.value = 0
        self.ids.prg_lab.text = "0% progress"

    def start_loading(self):
        Clock.schedule_once(self.update_progress, 1)

    def update_progress(self, dt):
        curr = self.ids.prg_bar.value
        curr += 0.1
        self.ids.prg_bar.value = curr
        self.ids.prg_lab.text = f"{int(curr * 100)}% progress"

        if curr < 1.0:
            Clock.schedule_once(self.update_progress, 1)
        else:
            app = App.get_running_app()
            app.root.current = "recommended"


class RecommendedProducts(Screen):
    def switch_to_first_screen(self):
        screen_manager = self.manager
        screen_manager.current = 'welcome'

    def on_enter(self):
        self.clear_carousel()
        self.setup_carousel()

    def setup_carousel(self):
        names = ["John", "Emily", "Michael", "Sophia"]

        carousel = Carousel(direction='right')
        carousel.clear_widgets()

        screen_width = Window.width
        font_size = int(screen_width / 30)

        for name in names:
            label = Label(text=name, font_size=font_size, color=(0, 0, 0, 1))
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
