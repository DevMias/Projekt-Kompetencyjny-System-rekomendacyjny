from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


class Welcome(Screen):
    pass


class ChoosePerson(Screen):
    pass


class ChooseRecommendationMethod(Screen):
    pass


class LoadingScreen(Screen):
    def start_loading(self):  # tu metoda która będzie bawić się tą rekomendacją
        curr = self.ids.prg_bar.value
        curr += .25
        self.ids.prg_bar.value = curr
        self.ids.prg_lab.text = f'{int(curr*100)}% progress'
        if self.ids.prg_bar.value == 1:
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
