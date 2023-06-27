from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.lang import Builder


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
    def build(self):
        names = ["John", "Emily", "Michael", "Sophia"]

        kv = Builder.load_file('recommend.kv')

        carousel = kv.ids.carousel

        carousel.clear_widgets()

        for name in names:
            label = Label(text=name, font_size=20, color=(0, 0, 0, 1))
            carousel.add_widget(label)

        return kv

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


class WindowManager(ScreenManager):
    pass


class RecommendApp(App):
    def build(self):
        Window.minimum_width = 800
        Window.minimum_height = 600

        return WindowManager()

    def reset_app(self):
        self.stop()


if __name__ == '__main__':
    RecommendApp().run()
