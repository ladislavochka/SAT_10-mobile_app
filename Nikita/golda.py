
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
import random

class Youtube(App):
    def build(self):
        self.shorts_ideas = [
            "Logika - це платформа для казіно",
            "Чорноморськ - це гетто-село"
        ]
        self.videos_ideas = [
            "Феномен Бурмолди",
            "Домовенок в прaймі"
        ]
        self.current_format = "Shorts"
        self.current_idea = None
        self.dark_theme = False
        main_layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )
        with main_layout.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=(0, 0), size=(1600, 1200))
        header = Label(
            text="Youtube Studio Helper",
            font_size="20sp",
            bold=True,
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=45
        )
        main_layout.add_widget(header)
        self.header = header
        self.format_label = Label(
            text="Обраний формат: Shorts",
            font_size="14sp",
            bold=True,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(self.format_label)
        btn_layout = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=45
        )
        shorts_btn = Button(
            text="Shorts",
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1),
            font_size="15sp",
            bold=True
        )
        shorts_btn.bind(on_press=self.set_shorts)
        btn_layout.add_widget(shorts_btn)
        self.shorts_btn = shorts_btn
        video_btn = Button(
            text="Video",
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0, 0, 0, 1),
            font_size="15sp"
        )
        video_btn.bind(on_press=self.set_video)
        btn_layout.add_widget(video_btn)
        self.video_btn = video_btn
        main_layout.add_widget(btn_layout)
        self.result_label = Label(
            text="Натисни для генерації ідеї",
            font_size="16sp",
            color=(0.1, 0.1, 0.1, 1),
            halign="center",
            text_size=(320, None)
        )
        main_layout.add_widget(self.result_label)
        generate_btn = Button(
            text="Generate an idea",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=55,
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        generate_btn.bind(on_press=self.generate_idea)
        main_layout.add_widget(generate_btn)
        self.theme_btn = Button(
            text="Увімкнути темну тему",
            size_hint_y=None,
            height=45
        )
        self.theme_btn.bind(on_press=self.toggle_theme)
        main_layout.add_widget(self.theme_btn)
        self.delete_btn = Button(
            text="Видалити поточну ідею",
            size_hint_y=None,
            height=45,
            background_color=(0.8, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.delete_btn.bind(on_press=self.delete_idea)
        main_layout.add_widget(self.delete_btn)

        return main_layout

    def set_shorts(self, instance):
        self.current_format = "Shorts"
        self.current_idea = None
        self.format_label.text = "Обраний формат: Shorts"
        self.result_label.text = "Формат змінено на Shorts"
        self.update_format_buttons()

    def set_video(self, instance):
        self.current_format = "Video"
        self.current_idea = None
        self.format_label.text = "Обраний формат: Video"
        self.result_label.text = "Формат змінено на Video"
        self.update_format_buttons()

    def generate_idea(self, instance):
        if self.current_format == "Shorts":
            idea = random.choice(self.shorts_ideas)
        else:
            idea = random.choice(self.videos_ideas)

        self.current_idea = idea
        self.result_label.text = f"Idea: \n\n{idea}"

    def toggle_theme(self, instance):
        self.dark_theme = not self.dark_theme

        if self.dark_theme:
            self.bg_color.rgba = (0.08, 0.08, 0.10, 1)
            self.header.color = (1, 0.2, 0.2, 1)
            self.format_label.color = (0.8, 0.8, 0.8, 1)
            self.result_label.color = (1, 1, 1, 1)

            self.theme_btn.text = "Увімкнути світлу тему"
            self.theme_btn.background_color = (0.25, 0.25, 0.3, 1)
            self.theme_btn.color = (1, 1, 1, 1)

            self.shorts_btn.color = (1, 1, 1, 1)
            self.video_btn.color = (1, 1, 1, 1)

        else:
            self.bg_color.rgba = (1, 1, 1, 1)
            self.header.color = (1, 0, 0, 1)
            self.format_label.color = (0.4, 0.4, 0.4, 1)
            self.result_label.color = (0.1, 0.1, 0.1, 1)

            self.theme_btn.text = "Увімкнути темну тему"
            self.theme_btn.background_color = (0.8, 0.8, 0.8, 1)
            self.theme_btn.color = (0, 0, 0, 1)

        self.update_format_buttons()

    def update_format_buttons(self):
        if self.current_format == "Shorts":
            self.shorts_btn.background_color = (1, 0, 0, 1)
            self.video_btn.background_color = (
                (0.25, 0.25, 0.3, 1)
                if self.dark_theme else (0.8, 0.8, 0.8, 1)
            )
        else:
            self.video_btn.background_color = (1, 0, 0, 1)
            self.shorts_btn.background_color = (
                (0.25, 0.25, 0.3, 1)
                if self.dark_theme else (0.8, 0.8, 0.8, 1)
            )
        if not self.dark_theme:
            self.shorts_btn.color = (
                (1, 1, 1, 1)
                if self.current_format == "Shorts"
                else (0, 0, 0, 1)
            )
            self.video_btn.color = (
                (1, 1, 1, 1)
                if self.current_format == "Video"
                else (0, 0, 0, 1)
            )

    def delete_idea(self, instance):
        if self.current_idea is None:
            self.result_label.text = (
                "Спочатку згенеруй ідею, яку хочеш видалити!"
            )
            return

        if self.current_format == "Shorts":
            ideas = self.shorts_ideas
        else:
            ideas = self.videos_ideas
        if self.current_idea in ideas:
            ideas.remove(self.current_idea)
            self.result_label.text = (
                f"Ідею видалено:\n\n{self.current_idea}"
            )
            self.current_idea = None
        else:
            self.result_label.text = "Цієї ідеї вже немає у списку."
            self.current_idea = None


Youtube().run()