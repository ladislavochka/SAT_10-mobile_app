from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import random

class Youtube(App):
    def build(self):
        self.shorts_ideas = ["Logika - це платформа для казіно","Чорноморськ - це гетто-село",
                             "Я 24 години будував будинок у Minecraft і не вийшов з гри",
                             "Паперовий літак проти реактивного: хто далі?",
                             "Козаки були крутіші за супергероїв: 5 фактів",
                             "Кіт став директором казіно і розорив усіх",
                             "Якби президентом став кіт: перша постанова про корм",
                             "Вибори в класі: хто обіцяв найбільше і виконав найменше",
                             "Roblox: я зробив найдивнішу гру за 10 хвилин",
                             "Найкращий геймер світу програв бабусі в шахи"]
        self.videos_ideas = ["Феномен Бурмолди","Домовенок в прaймі",
                             "Minecraft, але кожні 5 хвилин блоки стають піцою",
                             "Танк проти трактора: хто виживе в українському полі?",
                             "Історія борщу: війна за мільйони тарілок",
                             "Я тиждень жив як домовенок у власній квартирі",
                             "Як працюють вибори: пояснюю на прикладі шкільного буфету",
                             "Фейки в політиці: розбираємо вірусні вигадки",
                             "Топ-5 ігор, у яких я програв усі нерви",
                             "GTA в реальному житті: що буде, якщо ігнорувати світлофори?"]
        self.current_format = "Shorts"
        self.step = 0
        self.total_steps = 25
        self.pixel_colors = [(0.5,0.8,1,1), (1,1,1,1), (1,0.9,0.1,1), (0.2,0.7,0.2,1), (0.5,0.3,0.1,1),
                             (0.7,0.7,0.7,1), (0.35,0.4,0.35,1), (0,0,0,1), (0.9,0.1,0.1,1), (0.95,0.6,0.2,1)]
        self.theme_names = ["Minecraft", "відеоігри", "політика", "історія", "військова тематика", "казино", "загальна тема"]
        self.theme_bonuses = [20, 18, 10, 12, 15, 5, 3]
        self.theme_levels = [2, 2, 3, 3, 3, 3, 2]
        self.theme_audiences = ["Школярі й підлітки 10-17 років, фанати ігор.", "Підлітки 10-25 років, любителі стрімів.",
                                "Старшокласники й дорослі 16+, яких цікавлять новини.",
                                "Учні й студенти, які люблять дізнаватися нове.",
                                "Підлітки й дорослі, яких цікавить техніка.",
                                "Дорослі 18+, яких цікавлять онлайн-платформи.",
                                "Широка аудиторія 13-30 років, яка любить жарти."]
        self.theme_tips = ["Покажи найкумедніший момент уже в перші секунди.", "Покажи смішний момент на початку.",
                           "Показуй факти з перевірених джерел і різні думки, без образ.",
                           "Додай карти або смішні порівняння, щоб було легше пояснити.",
                           "Перевір факти й дати та вкажи, де ти їх знайшов.",
                           "Не рекламуй азартні ігри й перевір факти, щоб не ввести в оману.",
                           "Додай у назву слово, яке пояснює, про що буде відео."]
        self.pictures = [
            ["000000002200","001100022220","000000000000","033300000000","033300000000","004000000000","333333333333","445444464444"],
            ["000000000000","006666666600","066766662660","067776636860","066766661660","006666666600","000660066000","000000000000"],
            ["000000000000","000001110000","000001110000","066677776660","066666666660","066662266660","066666666660","333333333333"],
            ["000000000000","505000000505","555000000555","555050050555","555555555555","557555555575","555554455555","333333333333"],
            ["000006600000","000005500000","066666666660","000668866000","000006600000","000006600000","000066660000","000000000000"],
            ["333333333333","338888888833","338188881833","338888888833","338881188833","338188881833","338888888833","333333333333"],
            ["555555555555","588881888885","588881188885","588881118885","588881118885","588881188885","588881888885","555555555555"]]
        self.root_box = BoxLayout()
        main_layout = BoxLayout(orientation="vertical", padding = 20, spacing=10)
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=(0, 0), size=(1600, 1200))
        header = Label(text = "Youtube Studio Helper", font_size="20sp", bold = True,
                       color=(1,0,0,1), size_hint_y= None, height= 45)
        main_layout.add_widget(header)
        self.format_label = Label(text="Обраний формат: Shorts", font_size="14sp", bold=True, color=(0.4,0.4,0.4, 1), size_hint_y=None, height=30)
        main_layout.add_widget(self.format_label)
        btn_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height = 45)
        self.shorts_btn = Button(text="Shorts", background_color=(1,0,0,1), color=(1,1,1,1),
                            font_size="15sp", bold = True)
        self.shorts_btn.bind(on_press=self.set_shorts)
        btn_layout.add_widget(self.shorts_btn)
        self.video_btn = Button(text="Video", background_color=(0.8, 0.8, 0.8, 1),
                           color=(0,0,0, 1), font_size="15sp")
        self.video_btn.bind(on_press=self.set_video)
        btn_layout.add_widget(self.video_btn)
        main_layout.add_widget(btn_layout)
        self.result_label = Label(text = "Натисни для генерації ідеї", font_size="16sp", color=(0.1,0.1,0.1,1),
                                  halign = 'center', text_size = (320, None))
        main_layout.add_widget(self.result_label)
        self.pixel_box = BoxLayout(size_hint_y=None, height=160)
        self.pixel_box.bind(pos=self.draw_pixels, size=self.draw_pixels)
        main_layout.add_widget(self.pixel_box)
        self.analysis_btn = Button(text="Перспективи відео", font_size="16sp", bold=True,
                                   size_hint_y=None, height=50, background_color=(0.1,0.5,0.9,1),
                                   color=(1,1,1,1))
        self.analysis_btn.bind(on_press=self.show_command_center)
        main_layout.add_widget(self.analysis_btn)
        self.generate_btn = Button(text = "Generate an idea", font_size="16sp", bold = True,
                              size_hint_y=None, height= 55, background_color=(1,0,0,1),
                              color=(1,1,1,1))
        self.generate_btn.bind(on_press=self.generate_idea)
        main_layout.add_widget(self.generate_btn)
        self.main_layout = main_layout
        self.root_box.add_widget(main_layout)
        self.hide_result()
        return self.root_box
    def set_shorts(self, instance):
        self.current_format = "Shorts"
        self.format_label.text = "Обраний формат: Shorts"
        self.hide_result()
        self.result_label.text = "Формат змінено на Shorts"
    def set_video(self, instance):
        self.current_format = "Video"
        self.format_label.text = "Обраний формат: Video"
        self.hide_result()
        self.result_label.text = "Формат змінено на Video"
    def generate_idea(self, instance):
        if self.current_format == "Shorts":
            idea = random.choice(self.shorts_ideas)
        else:
            idea = random.choice(self.videos_ideas)
        self.current_idea = idea
        self.current_theme = self.get_theme(idea)
        self.hide_result()
        self.shorts_btn.disabled = True
        self.video_btn.disabled = True
        self.generate_btn.disabled = True
        self.step = 0
        self.anim_event = Clock.schedule_interval(self.animation_step, 0.1)
    def animation_step(self, dt):
        self.step = self.step + 1
        percent = self.step * 100 // self.total_steps
        if percent < 30:
            status = "Аналізую тему..."
        elif percent < 70:
            status = "Малюю піксельну картинку..."
        else:
            status = "Дорисовую деталі..."
        bar = "#" * (percent // 10) + "-" * (10 - percent // 10)
        typed = self.current_idea[:len(self.current_idea) * self.step // self.total_steps]
        self.result_label.text = f"{status}\n[{bar}] {percent}%\n\n{typed}"
        self.pixels = self.make_noisy_picture(percent)
        self.draw_pixels()
        if self.step >= self.total_steps:
            self.anim_event.cancel()
            self.result_label.text = f"Idea: \n\n{self.current_idea}"
            self.analysis_btn.opacity = 1
            self.analysis_btn.disabled = False
            self.shorts_btn.disabled = False
            self.video_btn.disabled = False
            self.generate_btn.disabled = False
    def make_noisy_picture(self, percent):
        picture = self.pictures[self.current_theme]
        noisy = []
        for row in picture:
            line = ""
            for digit in row:
                if random.randint(1, 100) <= percent:
                    line = line + digit
                else:
                    line = line + str(random.randint(0, 9))
            noisy.append(line)
        return noisy
    def hide_result(self):
        self.analysis_btn.opacity = 0
        self.analysis_btn.disabled = True
        self.pixels = []
        self.draw_pixels()
    def draw_pixels(self, *args):
        self.pixel_box.canvas.clear()
        if len(self.pixels) == 0:
            return
        cell = int(min(self.pixel_box.width / 12, self.pixel_box.height / 8))
        if cell < 2:
            return
        start_x = self.pixel_box.x + (self.pixel_box.width - cell * 12) / 2
        start_y = self.pixel_box.y + (self.pixel_box.height - cell * 8) / 2
        with self.pixel_box.canvas:
            for row in range(8):
                for col in range(12):
                    Color(*self.pixel_colors[int(self.pixels[row][col])])
                    Rectangle(pos=(start_x + col * cell, start_y + (7 - row) * cell),
                              size=(cell - 1, cell - 1))
    def get_theme(self, idea):
        text = idea.lower()
        if "minecraft" in text:
            return 0
        elif "roblox" in text or "fortnite" in text or "gta" in text or "геймер" in text or "ігор" in text:
            return 1
        elif "політи" in text or "вибор" in text or "президент" in text or "закон" in text or "фейк" in text:
            return 2
        elif "історі" in text or "козак" in text or "замк" in text:
            return 3
        elif "літак" in text or "танк" in text or "війн" in text:
            return 4
        elif "казіно" in text:
            return 5
        else:
            return 6
    def get_score(self):
        score = 50 + self.theme_bonuses[self.current_theme]
        if self.current_format == "Shorts":
            score = score + 5
        if len(self.current_idea) <= 35:
            score = score + 10
        elif len(self.current_idea) > 50:
            score = score - 5
        for word in ["феномен", "супергер", "проти", "але ", "експеримент", "історі", "фейк", "roblox"]:
            if word in self.current_idea.lower():
                score = score + 5
        if score > 100:
            score = 100
        return score
    def show_command_center(self, instance):
        score = self.get_score()
        level = self.theme_levels[self.current_theme]
        if self.current_format == "Video":
            level = level + 1
        if score >= 75:
            verdict = "Високий потенціал: тема весела і має гарні шанси зацікавити."
        elif score >= 55:
            verdict = "Середній потенціал: ідею варто зробити яскравішою."
        else:
            verdict = "Низький потенціал: ідею потрібно доопрацювати."
        if self.current_format == "Shorts":
            structure = "1. Вступ: гачок у перші 3 секунди.\n2. Основна частина: одна думка за 30 с.\n3. Завершення: жарт і запитання."
        else:
            structure = "1. Вступ: інтрига до 30 с.\n2. Основна частина: 3-4 блоки.\n3. Завершення: підсумок і підписка."
        tips = "- " + self.theme_tips[self.current_theme]
        if score < 55:
            tips = tips + "\n- Зроби назву конкретнішою та цікавішою."
        bar = "#" * (score // 10) + "-" * (10 - score // 10)
        info_text = (f"{self.current_idea}\n\n[color=ff0000][b]Потенціал: {score} / 100\n|{bar}|[/b][/color]\n\n"
                     f"Аналіз: тема - {self.theme_names[self.current_theme]}.\n{verdict}\n\n"
                     f"Аудиторія: {self.theme_audiences[self.current_theme]}\n\n"
                     f"Складність створення: {level} з 5\n\nСтруктура відео:\n{structure}\n\n"
                     f"Поради:\n{tips}\n\nЦе проста оцінка за правилами програми, а не прогноз YouTube.")
        command_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        with command_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect2 = Rectangle(pos=(0, 0), size=(1600, 1200))
        command_layout.add_widget(Label(text="YouTube Command Center", font_size="20sp", bold=True,
                                        color=(1,0,0,1), size_hint_y=None, height=45))
        info_label = Label(text=info_text, font_size="14sp", color=(0.1,0.1,0.1,1), halign="left", markup=True,
                           valign="top", size_hint=(None, None), text_size=(320, None))
        info_label.bind(texture_size=info_label.setter("size"))
        scroll = ScrollView()
        scroll.add_widget(info_label)
        command_layout.add_widget(scroll)
        back_btn = Button(text="Назад", font_size="16sp", bold=True, size_hint_y=None, height=55,
                          background_color=(1,0,0,1), color=(1,1,1,1))
        back_btn.bind(on_press=self.go_back)
        command_layout.add_widget(back_btn)
        self.root_box.clear_widgets()
        self.root_box.add_widget(command_layout)
    def go_back(self, instance):
        self.root_box.clear_widgets()
        self.root_box.add_widget(self.main_layout)
Youtube().run()
