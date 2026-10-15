import json
import os
import re
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


BG = (0.055, 0.055, 0.09, 1)
SIDEBAR_BG = (0.075, 0.07, 0.12, 1)
PANEL_BG = (0.09, 0.085, 0.14, 1)
PURPLE = (0.48, 0.30, 0.95, 1)
BUBBLE_AI = (0.13, 0.12, 0.20, 1)
BUBBLE_USER = (0.29, 0.20, 0.53, 1)
WHITE = (0.94, 0.93, 1, 1)


def set_background(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)

    widget.bind(
        pos=lambda instance, value: setattr(rect, 'pos', value),
        size=lambda instance, value: setattr(rect, 'size', value)
    )


class AI:

    def __init__(self):
        self.file = 'brain.json'

        if os.path.exists(self.file):
            with open(self.file, 'r', encoding='utf-8') as file:
                self.brain = json.load(file)
        else:
            self.brain = {
                'привіт': 'Привіт! Чим я можу допомогти?'
            }

            with open(self.file, 'w', encoding='utf-8') as file:
                json.dump(
                    self.brain, file,
                    ensure_ascii=False, indent=4
                )

    def words(self, text):
        text = text.lower()
        words = re.findall(
            r'[а-щьюяєіїґa-z0-9]+', text
        )

        stop_words = {
            'і', 'й', 'та', 'ще', 'що', 'як', 'у', 'в'
        }

        return {
            word for word in words
            if word not in stop_words
        }

    def similarity(self, text1, text2):
        words1 = self.words(text1)
        words2 = self.words(text2)

        if not words1 or not words2:
            return 0

        return (
            len(words1.intersection(words2))
            / max(len(words1), len(words2))
        )

    def get_answer(self, question):
        best_answer = None
        best_score = 0

        for saved_question, answer in self.brain.items():
            score = self.similarity(
                question, saved_question
            )

            if score > best_score:
                best_score = score
                best_answer = answer

        if best_score >= 0.35:
            return best_answer, best_score

        return None, best_score

    def teach(self, question, answer):
        self.brain[question.lower()] = answer

        with open(self.file, 'w', encoding='utf-8') as file:
            json.dump(
                self.brain, file,
                ensure_ascii=False, indent=4
            )


class ChatBoormolda(App):

    def build(self):
        self.ai = AI()
        self.learning_mode = None
        self.learning_question = None

        main = BoxLayout(orientation='horizontal')
        set_background(main, BG)

        sidebar = BoxLayout(
            orientation='vertical',
            size_hint_x=0.25,
            padding=10,
            spacing=10
        )
        set_background(sidebar, SIDEBAR_BG)

        logo = Label(
            text='[b]ChatBoormolda[/b]',
            markup=True,
            font_size=22,
            color=WHITE,
            size_hint_y=None,
            height=55
        )
        sidebar.add_widget(logo)

        new_chat = Button(
            text='＋  New Chat',
            size_hint_y=None,
            height=45,
            background_normal='',
            background_color=PURPLE,
            color=WHITE
        )
        new_chat.bind(on_press=self.button_animation)
        new_chat.bind(on_press=self.new_chat)
        sidebar.add_widget(new_chat)

        teach_button = Button(
            text='✦  Навчити ШІ',
            size_hint_y=None,
            height=42,
            background_normal='',
            background_color=(0.20, 0.16, 0.32, 1),
            color=WHITE
        )
        teach_button.bind(on_press=self.button_animation)
        teach_button.bind(on_press=self.start_learning)
        sidebar.add_widget(teach_button)

        for text in ['Python', 'Kivy', 'Навчання']:
            chat = Button(
                text=text,
                size_hint_y=None,
                height=40,
                background_normal='',
                background_color=(0.12, 0.11, 0.18, 1),
                color=WHITE
            )
            chat.bind(on_press=self.button_animation)
            sidebar.add_widget(chat)

        sidebar.add_widget(Label())

        content = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=10
        )
        set_background(content, BG)

        header = Label(
            text='[b]ChatBoormolda[/b]',
            markup=True,
            font_size=26,
            color=WHITE,
            size_hint_y=None,
            height=60
        )
        content.add_widget(header)

        self.messages_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=(5, 10)
        )

        self.messages_box.bind(
            minimum_height=self.messages_box.setter('height')
        )

        self.scroll = ScrollView(
            bar_width=5,
            scroll_type=['bars', 'content'],
            bar_color=PURPLE,
            bar_inactive_color=(0.3, 0.25, 0.4, 0.5)
        )

        self.scroll.add_widget(self.messages_box)
        content.add_widget(self.scroll)

        bottom = BoxLayout(
            size_hint_y=None,
            height=55,
            spacing=10
        )

        self.input = TextInput(
            hint_text='Напиши повідомлення...',
            multiline=False,
            foreground_color=WHITE,
            hint_text_color=(0.6, 0.58, 0.7, 1),
            cursor_color=PURPLE,
            background_normal='',
            background_active='',
            background_color=PANEL_BG,
            padding=(15, 15),
            font_size=16
        )

        self.input.bind(
            on_text_validate=self.send_message
        )

        send = Button(
            text='➤',
            size_hint_x=None,
            width=55,
            background_normal='',
            background_color=PURPLE,
            color=WHITE,
            font_size=22
        )

        send.bind(on_press=self.button_animation)
        send.bind(on_press=self.send_message)

        bottom.add_widget(self.input)
        bottom.add_widget(send)
        content.add_widget(bottom)

        main.add_widget(sidebar)
        main.add_widget(content)

        self.add_message(
            'Boormolda:\nГотовий відповісти на будь-які питання!'
        )

        main.opacity = 0
        Animation(opacity=1, duration=0.5).start(main)

        return main

    def button_animation(self, button):
        Animation.cancel_all(button, 'opacity')

        animation = (
            Animation(opacity=0.7, duration=0.06)
            + Animation(opacity=1, duration=0.15)
        )

        animation.start(button)

    def start_learning(self, instance):
        self.learning_mode = 'question'
        self.learning_question = None

        self.add_message(
            'Boormolda:\n'
            'Введіть запитання, якому ви хочете мене навчити:'
        )

    def send_message(self, instance):
        text = self.input.text.strip()

        if not text:
            return

        self.add_message('Ти:\n' + text)
        self.input.text = ''

        if self.learning_mode == 'question':
            self.learning_question = text
            self.learning_mode = 'answer'

            self.add_message(
                'Boormolda:\n'
                'Тепер введіть відповідь на це запитання:'
            )
            return

        if self.learning_mode == 'answer':
            self.ai.teach(self.learning_question, text)

            self.add_message(
                'Boormolda:\nДякую! Я запам’ятав відповідь.'
            )

            self.learning_question = None
            self.learning_mode = None
            return

        answer, score = self.ai.get_answer(text)

        if answer:
            self.add_message(
                'ChatBoormolda:\n' + answer
            )
        else:
            self.learning_question = text
            self.learning_mode = 'answer'

            self.add_message(
                'ChatBoormolda:\n'
                'Я не знаю відповіді. Напишіть правильну '
                'відповідь, щоб навчити мене:'
            )

    def add_message(self, text):
        is_user = text.startswith('Ти:\n')

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            spacing=5
        )

        bubble = BoxLayout(
            orientation='vertical',
            size_hint_x=0.88,
            size_hint_y=None,
            padding=(12, 10)
        )

        bubble_color = BUBBLE_USER if is_user else BUBBLE_AI
        set_background(bubble, bubble_color)

        label = Label(
            text=text,
            color=WHITE,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=16
        )

        label.bind(
            width=lambda instance, value: setattr(
                instance, 'text_size', (value, None)
            )
        )

        label.bind(
            texture_size=lambda instance, value: setattr(
                instance, 'height', value[1]
            )
        )

        bubble.add_widget(label)

        bubble.bind(
            minimum_height=bubble.setter('height')
        )

        row.bind(
            minimum_height=row.setter('height')
        )

        if is_user:
            row.add_widget(Label())
            row.add_widget(bubble)
        else:
            row.add_widget(bubble)
            row.add_widget(Label())

        self.messages_box.add_widget(row)

        row.opacity = 0

        Animation(
            opacity=1,
            duration=0.25
        ).start(row)

        Clock.schedule_once(
            lambda dt: setattr(self.scroll, 'scroll_y', 0),
            0.1
        )

    def new_chat(self, instance):
        self.messages_box.clear_widgets()

        self.learning_mode = None
        self.learning_question = None

        self.add_message(
            'Boormolda:\nНовий чат розпочато!'
        )


if __name__ == '__main__':
    ChatBoormolda().run()