from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
    pass


class ChooseRecommendationMethod(Screen):
    pass


class LoadingScreen(Screen):

    @staticmethod
    def start_loading():  # tu metoda która będzie bawić się tą rekomendacją
        app = App.get_running_app()
        screen_manager = app.root.ids.screen_manager
        screen_manager.current = 'recommended'


class RecommendedProducts(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class RecommendApp(App):
    def build(self):
        return WindowManager()


if __name__ == '__main__':
    RecommendApp().run()
