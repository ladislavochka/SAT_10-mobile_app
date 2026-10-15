import json, os, re
from kivy.app import App
from kivy.animation import Animation  #add
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

class AI:
    def __init__(self):
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brain.json")
        if os.path.exists(self.file):
            self.load_brain()
        else:
            self.brain = {
                "привіт": "Привіт! Радий тебе бачити 😊",
                "як справи": "У мене все добре! Я продовжую навчатися 🧠",
                "python": "Python — чудова мова програмування.",
                "kivy": "Kivy дозволяє створювати графічні застосунки."
            }
            self.save_brain()

    def load_brain(self):
        try:
            with open(self.file, "r", encoding="utf-8") as file:
                self.brain = json.load(file)
        except:
            self.brain = {}

    def save_brain(self):
        with open(self.file, "w", encoding="utf-8") as file:
            json.dump(self.brain,file,ensure_ascii=False,indent=4)

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
            score = self.similarity(question,saved_question)
            if score > best_score:
                best_score = score
                best_answer = answer
        return (best_answer,best_score) if best_score >= 0.35 else (None, best_score)

    def teach(self, question, answer):
        self.brain[question.lower()] = answer
        self.save_brain()

class ChatGPT(App):
    def build(self):
        self.ai = AI()
        self.learning_mode = None
        self.learning_question = None
        main = BoxLayout(orientation="horizontal")
        sidebar = BoxLayout(orientation="vertical",size_hint_x=0.25,padding=10,spacing=10)
        logo = Label(text="ChatGPT",font_size=22,size_hint_y=None,height=50)
        sidebar.add_widget(logo)
        new_chat = Button(text="+ New chat",size_hint_y=None,height=45)
        new_chat.bind(on_press=self.new_chat)
        sidebar.add_widget(new_chat)
        teach_button = Button(text="🧠 Навчити ШІ",size_hint_y=None,height=40)
        teach_button.bind(on_press=self.start_learning)
        sidebar.add_widget(teach_button)
        for text in ["Python", "Kivy", "Навчання"]:
            chat = Button(text=text,size_hint_y=None,height=40)
            # add
            chat.bind(on_press=self.button_animation)#Коли курсор натискає кнопку,вона трохи зменшується.
            #add
            sidebar.add_widget(chat)
        sidebar.add_widget(Label())
        content = BoxLayout(orientation="vertical",padding=20)
        header = Label(text="Cha tGPT",font_size=26,size_hint_y=None,height=60)
        content.add_widget(header)
        self.messages = BoxLayout(orientation="vertical",size_hint_y=None,spacing=15)
        self.messages.bind(minimum_height=self.messages.setter("height"))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.messages)
        content.add_widget(self.scroll)
        bottom = BoxLayout(size_hint_y=None,height=55,spacing=10)
        self.input = TextInput(hint_text="Message ChatGPT...",multiline=False)
        self.input.bind(on_text_validate=self.send_message)
        send = Button(text="➤",size_hint_x=None,width=55)
        #add
        send.bind(on_press=self.button_animation)#Коли курсор натискає кнопку,вона трохи зменшується.
        #add
        send.bind(on_press=self.send_message)
        bottom.add_widget(self.input)
        bottom.add_widget(send)
        content.add_widget(bottom)
        main.add_widget(sidebar)
        main.add_widget(content)
        self.add_message("ChatGPT\nПривіт! Я локальний ШІ з пам'яттю 🧠")
        #add
        Animation(opacity=1,duration=0.5).start(main)# При запуску трохи збільшуємо головне вікно.
        #add
        return main
    #add
    def button_animation(self, button):
        # Зберігаємо початковий розмір кнопки
        old_width = button.width
        old_height = button.height
        # Зменшуємо кнопку на момент натискання
        animation = Animation(size_hint_x=0.95,duration=0.08)
        # Після анімації повертаємо її назад
        animation += Animation(size_hint_x=1,duration=0.08)
        animation.start(button)
    #add
    def start_learning(self, instance):
        self.learning_mode = "question"
        self.learning_question = None
        self.add_message(
            "ChatGPT\nДобре 🧠 Напиши питання, "
            "якому хочеш мене навчити.")
    def send_message(self, instance):
        text = self.input.text.strip()
        if not text:
            return
        self.add_message("You\n" + text)
        self.input.text = ""
        if self.learning_mode == "question":
            self.learning_question = text
            self.learning_mode = "answer"
            self.add_message(
                "ChatGPT\nТепер напиши правильну "
                "відповідь на це питання.")
            return

        if self.learning_mode == "answer":
            self.ai.teach(self.learning_question,text)
            self.add_message("ChatGPT\nГотово! 🧠 Я запам'ятав це.")
            self.learning_mode = None
            self.learning_question = None
            return
        answer, score = self.ai.get_answer(text)

        if answer:
            self.add_message(
                f"ChatGPT\n{answer}\n\n"
                f"Схожість: {int(score * 100)}%")
        else:
            self.learning_question = text
            self.learning_mode = "answer"
            self.add_message(
                "ChatGPT\nЯ ще не знаю відповіді "
                "на це питання 🤔\n"
                "Напиши правильну відповідь, "
                "і я її запам'ятаю.")

    def add_message(self, text):
        label = Label(text=text,size_hint_y=None,halign="left",valign="top")
        label.bind(texture_size=lambda obj, size:setattr(obj, "height", size[1] + 20))
        self.messages.add_widget(label)
        # add
        label.opacity = 0# Повідомлення спочатку прозоре.
        Animation(opacity=1,duration=0.25).start(label)# Потім плавно з'являється.
        #add
        self.scroll.scroll_y = 0

    def new_chat(self, instance):
        self.messages.clear_widgets()
        self.learning_mode = None
        self.learning_question = None
        self.add_message("ChatGPT\nНовий чат створено 🧠")

ChatGPT().run()