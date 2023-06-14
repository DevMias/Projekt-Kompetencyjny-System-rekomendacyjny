from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
    pass


class ChooseRecommendationMethod(Screen):
    pass


class LoadingScreen(Screen):
    def start_loading(self):
        Clock.schedule_once(self.update_progress, 1)

    def update_progress(self, dt):  # tutaj skrypt do rekomendacji
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
    pass


class WindowManager(ScreenManager):
    pass


class RecommendApp(App):
    def build(self):
        Window.minimum_width = 800
        Window.minimum_height = 600

        return WindowManager()

    def reset_app(self):  # mam problemik z resetem apki
        self.stop()


if __name__ == '__main__':
    RecommendApp().run()
