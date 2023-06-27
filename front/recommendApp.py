from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen


class WindowManager(ScreenManager):
    pass


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
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
        curr += 0.25
        self.ids.prg_bar.value = curr
        self.ids.prg_lab.text = f"{int(curr * 100)}% progress"

        if curr < 1.0:
            Clock.schedule_once(self.update_progress, 1)
        else:
            app = App.get_running_app()
            app.root.current = "recommended"


class RecommendedProducts(Screen):
    def switch_to_first_screen(self):
        window_manager = App.get_running_app().root
        window_manager.current = 'welcome'


class RecommendApp(App):
    def build(self):
        return WindowManager()


if __name__ == '__main__':
    RecommendApp().run()
