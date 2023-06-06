from kivy.app import App
from kivy.uix.widget import Widget


class Welcome(Widget):

    def button_pressed(self):
        pass


class RecommendApp(App):
    def build(self):
        return Welcome()


if __name__ == '__main__':
    RecommendApp().run()
