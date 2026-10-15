import json, os, re
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window  # ДОДАНО: налаштування фону вікна
from kivy.utils import get_color_from_hex  # ДОДАНО: зручне задання кольорів HEX

# ДОДАНО: палітра червоного інтерфейсу
RED = "#E53935"  # Основний червоний колір
DARK_RED = "#8E151B"  # Темно-червоний для бічної панелі
BG = "#1C1113"  # Темний фон чату з червонуватим відтінком
CARD = "#2B1B1E"  # Фон повідомлень і поля введення
WHITE = "#FFFFFF"  # Основний колір тексту
MUTED = "#D8BFC2"  # Приглушений колір тексту

class AI:
    def __init__(self):
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brain.json")
        if os.path.exists(self.file):
            self.load_brain()
        else:
            self.brain = {
                "привет": "Привет! Я Верити 😊",
                "як справи": "У мене все добре! Я продовжую навчатися 🧠",
                "python": "Python — чудова мова програмування.",
                "kivy": "Kivy дозволяє створювати графічні застосунки,йоу.",
                "где столица франции?": "ойвививи это Париж мерси",
                "67": "67"
            }
            self.save_brain()

    def load_brain(self):
        try:
            with open(self.file, "r", encoding="utf-8") as file:
                self.brain = json.load(file)
        except (json.JSONDecodeError, OSError):
            self.brain = {}

    def save_brain(self):
        with open(self.file, "w", encoding="utf-8") as file:
            json.dump(self.brain, file, ensure_ascii=False, indent=4)

    def words(self, text):
        text = text.lower()
        words = re.findall(r"[а-яіїєґa-z0-9]+", text)
        stop_words = {
            "і", "й", "та", "це", "що", "як",
            "у", "в", "на", "з", "до", "про",
            "мені", "ти"
        }
        return set(word for word in words if word not in stop_words)

    def similarity(self, text1, text2):
        words1 = self.words(text1)
        words2 = self.words(text2)
        if not words1 or not words2:
            return 0
        return len(words1.intersection(words2)) / max(len(words1), len(words2))

    def get_answer(self, question):
        best_answer = None
        best_score = 0
        for saved_question, answer in self.brain.items():
            score = self.similarity(question, saved_question)
            if score > best_score:
                best_score = score
                best_answer = answer
        return (best_answer, best_score) if best_score >= 0.35 else (None, best_score)

    def teach(self, question, answer):
        self.brain[question.lower()] = answer
        self.save_brain()

class ChatGPT(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(BG)  # ДОДАНО: темний фон вікна
        self.ai = AI()
        self.learning_mode = None
        self.learning_question = None
        main = BoxLayout(orientation="horizontal")
        with main.canvas.before:  # ДОДАНО: фон головного контейнера
            Color(*get_color_from_hex(BG))
            self.main_bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self.update_main_bg, size=self.update_main_bg)  # ДОДАНО: оновлення фону
        sidebar = BoxLayout(orientation="vertical", size_hint_x=0.25, padding=10, spacing=10)
        with sidebar.canvas.before:  # ДОДАНО: червоний фон бічної панелі
            Color(*get_color_from_hex(DARK_RED))
            self.sidebar_bg = Rectangle(pos=sidebar.pos, size=sidebar.size)
        sidebar.bind(pos=self.update_sidebar_bg, size=self.update_sidebar_bg)  # ДОДАНО
        logo = Label(text="[b]VERITY AI[/b]", markup=True, font_size=22, size_hint_y=None, height=50, color=get_color_from_hex(WHITE))  # ЗМІНЕНО: назва та колір
        sidebar.add_widget(logo)
        new_chat = Button(text="+ Новий чат", size_hint_y=None, height=45, background_normal="", background_color=get_color_from_hex(RED), color=get_color_from_hex(WHITE))  # ЗМІНЕНО: червона кнопка
        new_chat.bind(on_press=self.new_chat)
        sidebar.add_widget(new_chat)
        teach_button = Button(text="🧠 Навчити ШІ", size_hint_y=None, height=40, background_normal="", background_color=get_color_from_hex(RED), color=get_color_from_hex(WHITE))  # ЗМІНЕНО
        teach_button.bind(on_press=self.start_learning)
        teach_button.bind(on_press=self.button_animation)  # ДОДАНО: анімація натискання
        sidebar.add_widget(teach_button)
        for text in ["Python", "Kivy", "Навчання"]:
            chat = Button(text=text, size_hint_y=None, height=40, background_normal="", background_color=get_color_from_hex(CARD), color=get_color_from_hex(WHITE))  # ЗМІНЕНО: стиль кнопок меню
            chat.bind(on_press=self.button_animation)  # ДОДАНО: анімація натискання
            sidebar.add_widget(chat)
        sidebar.add_widget(Label())
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)
        with content.canvas.before:  # ДОДАНО: фон області чату
            Color(*get_color_from_hex(BG))
            self.content_bg = Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=self.update_content_bg, size=self.update_content_bg)  # ДОДАНО
        header = Label(text="[b]VERITY AI[/b]", markup=True, font_size=26, size_hint_y=None, height=60, color=get_color_from_hex(RED))  # ЗМІНЕНО: червоний заголовок
        content.add_widget(header)
        self.messages = BoxLayout(orientation="vertical", size_hint_y=None, spacing=15, padding=10)  # ЗМІНЕНО: додано відступи
        self.messages.bind(minimum_height=self.messages.setter("height"))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.messages)
        content.add_widget(self.scroll)
        bottom = BoxLayout(size_hint_y=None, height=55, spacing=10)
        self.input = TextInput(hint_text="Напиши повідомлення...", multiline=False, background_normal="", background_active="", background_color=get_color_from_hex(CARD), foreground_color=get_color_from_hex(WHITE), hint_text_color=get_color_from_hex(MUTED), cursor_color=get_color_from_hex(RED), padding=12)  # ЗМІНЕНО: оформлення поля введення
        self.input.bind(on_text_validate=self.send_message)
        send = Button(text="➤", size_hint_x=None, width=55, background_normal="", background_color=get_color_from_hex(RED), color=get_color_from_hex(WHITE))  # ЗМІНЕНО: червона кнопка надсилання
        send.bind(on_press=self.button_animation)  # ДОДАНО: анімація натискання
        send.bind(on_press=self.send_message)
        bottom.add_widget(self.input)
        bottom.add_widget(send)
        content.add_widget(bottom)
        main.add_widget(sidebar)
        main.add_widget(content)
        self.add_message("VERITY AI\nПривіт! Я локальний ШІ з пам'яттю 🧠")
        main.opacity = 0  # ЗМІНЕНО: початкове значення для плавної появи
        Animation(opacity=1, duration=0.5).start(main)  # ДОДАНО: плавна поява інтерфейсу
        return main

    # ДОДАНО: оновлення фону головного контейнера
    def update_main_bg(self, instance, value):
        self.main_bg.pos = instance.pos
        self.main_bg.size = instance.size

    # ДОДАНО: оновлення фону бічної панелі
    def update_sidebar_bg(self, instance, value):
        self.sidebar_bg.pos = instance.pos
        self.sidebar_bg.size = instance.size

    # ДОДАНО: оновлення фону області чату
    def update_content_bg(self, instance, value):
        self.content_bg.pos = instance.pos
        self.content_bg.size = instance.size

    # ДОДАНО: анімація натискання кнопок
    def button_animation(self, button):
        animation = Animation(opacity=0.7, duration=0.08) + Animation(opacity=1, duration=0.08)  # ЗМІНЕНО: плавне натискання без зміни розмірів
        animation.start(button)

    def start_learning(self, instance):
        self.learning_mode = "question"
        self.learning_question = None
        self.add_message("VERITY AI\nДобре 🧠 Напиши питання, якому хочеш мене навчити.")

    def send_message(self, instance):
        text = self.input.text.strip()
        if not text:
            return
        self.add_message("Ти\n" + text)
        self.input.text = ""
        if self.learning_mode == "question":
            self.learning_question = text
            self.learning_mode = "answer"
            self.add_message("VERITY AI\nТепер напиши правильну відповідь на це питання.")
            return
        if self.learning_mode == "answer":
            self.ai.teach(self.learning_question, text)
            self.add_message("VERITY AI\nГотово! 🧠 Я запам'ятав це.")
            self.learning_mode = None
            self.learning_question = None
            return
        answer, score = self.ai.get_answer(text)
        if answer:
            self.add_message(f"VERITY AI\n{answer}\n\nСхожість: {int(score * 100)}%")
        else:
            self.learning_question = text
            self.learning_mode = "answer"
            self.add_message("VERITY AI\nЯ ще не знаю відповіді на це питання 🤔\nНапиши правильну відповідь, і я її запам'ятаю.")

    def add_message(self, text):
        label = Label(text=text, size_hint_y=None, halign="left", valign="top", color=get_color_from_hex(WHITE), font_size=16)  # ЗМІНЕНО: світлий текст повідомлень
        label.bind(texture_size=lambda obj, size: setattr(obj, "height", size[1] + 20))
        label.bind(width=lambda obj, width: setattr(obj, "text_size", (width, None)))  # ДОДАНО: перенесення довгого тексту
        self.messages.add_widget(label)
        label.opacity = 0  # ЗМІНЕНО: повідомлення спочатку прозоре
        Animation(opacity=1, duration=0.25).start(label)  # ДОДАНО: плавна поява повідомлення
        self.scroll.scroll_y = 0

    def new_chat(self, instance):
        self.messages.clear_widgets()
        self.learning_mode = None
        self.learning_question = None
        self.add_message("VERITY AI\nНовий чат створено 🧠")

ChatGPT().run()