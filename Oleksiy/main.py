from datetime import date
import json
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, RoundedRectangle
INK = (0.055, 0.16, 0.23, 1)
DEEP = (0.035, 0.12, 0.18, 1)
CARD = (0.08, 0.22, 0.29, 1)
CARD_LIGHT = (0.10, 0.27, 0.34, 1)
MINT = (0.30, 0.88, 0.78, 1)
FOAM = (0.91, 0.97, 0.93, 1)
MUTED = (0.61, 0.76, 0.78, 1)
CORAL = (1.0, 0.52, 0.40, 1)
Bludo = [
    ("Овсяная каша на воде", 71),
    ("Гречка отварная", 110),
    ("Рис отварной", 130),
    ("Картофель отварной", 82),
    ("Картофельное пюре", 88),
    ("Макароны отварные", 157),
    ("Борщ", 50),
    ("Куриный суп с овощами", 45),
    ("Куриная грудка отварная", 165),
    ("Индейка запечённая", 150),
    ("Говядина тушёная", 220),
    ("Лосось запечённый", 206),
    ("Треска запечённая", 105),
    ("Яйцо варёное", 155),
    ("Омлет", 154),
    ("Творог 5%", 121),
    ("Йогурт натуральный", 63),
    ("Кефир 2,5%", 53),
    ("Салат греческий", 90),
    ("Винегрет", 130),
    ("Овощной салат с маслом", 120),
    ("Салат «Цезарь» с курицей", 190),
    ("Блины", 227),
    ("Сырники", 220),
    ("Вареники с картофелем", 150),
    ("Пельмени", 250),
    ("Пицца «Маргарита»", 250),
    ("Чизбургер", 295),
    ("Хлеб пшеничный", 265),
    ("Банановый смузи", 90),
]


def rounded_background(widget, color, radius=dp(22)):
    with widget.canvas.before:
        Color(*color)
        widget._background = RoundedRectangle(pos=widget.pos, size=widget.size,
                                               radius=[radius])
    widget.bind(pos=lambda obj, value: setattr(obj._background, "pos", value),
                size=lambda obj, value: setattr(obj._background, "size", value))

def label(text="", size=14, color=FOAM, bold=False, **kwargs):
    kwargs.setdefault("halign", "left")
    kwargs.setdefault("valign", "middle")
    return Label(text=text, font_size=sp(size), color=color, bold=bold,
                 **kwargs)

class ProgressRing(Widget):
    progress = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw, progress=self.redraw)
        self.redraw()
    def redraw(self, *_):
        self.canvas.clear()
        with self.canvas:
            cx, cy = self.center
            radius = min(self.width, self.height) * 0.39
            Color(0.20, 0.38, 0.42, 1)
            Line(circle=(cx, cy, radius, 0, 360), width=dp(10), cap="round")
            if self.progress > 0:
                Color(*MINT)
                Line(circle=(cx, cy, radius, -90, -90 + 360 * min(self.progress, 1)),
                     width=dp(10), cap="round")

class MealRow(BoxLayout):
    def __init__(self, meal, on_delete, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(58),
                         spacing=dp(10), padding=(dp(14), 0), **kwargs)
        rounded_background(self, CARD_LIGHT, dp(16))
        icon = label("◦", size=24, color=MINT, bold=True, size_hint_x=None, width=dp(22))
        self.add_widget(icon)
        text_col = BoxLayout(orientation="vertical", spacing=0)
        text_col.add_widget(label(meal.get("name", "Приём пищи"), size=14, bold=True))
        macros = " · ".join(f"{meal.get(k, 0)} г {name}" for k, name in
                            (("protein", "белка"), ("carbs", "углеводов"), ("fat", "жира"))
                            if meal.get(k, 0))
        text_col.add_widget(label(macros or "Добавлено сегодня", size=10, color=MUTED))
        self.add_widget(text_col)
        self.add_widget(label(f"{meal.get('kcal', 0)} ккал", size=13, bold=True,
                              size_hint_x=None, width=dp(76), halign="right"))
        remove = Button(text="×", size_hint=(None, None), size=(dp(30), dp(38)),
                        background_normal="", background_color=(0, 0, 0, 0),
                        color=MUTED, font_size=sp(20))
        remove.bind(on_release=lambda *_: on_delete())
        self.add_widget(remove)

class DishRow(BoxLayout):
    def __init__(self, name, kcal, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(56),
                         padding=(dp(16), dp(5)), spacing=dp(8), **kwargs)
        self.name_label = label(name, size=12, color=FOAM, text_size=(0, 0),
                                halign="left", valign="middle")
        self.name_label.bind(size=self._fit_name)
        self.add_widget(self.name_label)
        self.add_widget(label(f"≈ {kcal} ккал", size=12, color=MINT, bold=True,
                              size_hint_x=None, width=dp(92), halign="right"))

    def _fit_name(self, widget, size):
        widget.text_size = (max(0, size[0]), size[1])

class MealForm(ModalView):
    def __init__(self, on_save, **kwargs):
        super().__init__(size_hint=(0.90, None), height=dp(490), auto_dismiss=True,
                         background_color=(0, 0, 0, 0), **kwargs)
        self.on_save = on_save
        panel = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(22))
        rounded_background(panel, CARD, dp(26))
        panel.add_widget(label("Новая запись", size=21, bold=True, size_hint_y=None,
                               height=dp(36)))
        panel.add_widget(label("Что сегодня было вкусного?", size=13, color=MUTED,
                               size_hint_y=None, height=dp(24)))
        self.name_input = self.make_input("Например, овсянка с ягодами")
        panel.add_widget(self.field("Название", self.name_input))
        self.kcal_input = self.make_input("0", numeric=True)
        panel.add_widget(self.field("Калории (обязательно)", self.kcal_input))
        macro_row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(77))
        self.protein_input = self.make_input("0", numeric=True)
        self.carbs_input = self.make_input("0", numeric=True)
        self.fat_input = self.make_input("0", numeric=True)
        for title, field in (("Белки, г", self.protein_input),
                             ("Углев., г", self.carbs_input), ("Жиры, г", self.fat_input)):
            macro_row.add_widget(self.field(title, field))
        panel.add_widget(macro_row)
        panel.add_widget(Widget())
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel = Button(text="Отмена", background_normal="", background_color=CARD_LIGHT,
                        color=FOAM, font_size=sp(14))
        cancel.bind(on_release=lambda *_: self.dismiss())
        save = Button(text="Добавить", background_normal="", background_color=MINT,
                      color=INK, bold=True, font_size=sp(14))
        save.bind(on_release=self.save)
        buttons.add_widget(cancel)
        buttons.add_widget(save)
        panel.add_widget(buttons)
        self.add_widget(panel)
    @staticmethod
    def make_input(hint, numeric=False):
        return TextInput(hint_text=hint, multiline=False, input_filter="int" if numeric else None,
                         background_normal="", background_active="", background_color=CARD_LIGHT,
                         foreground_color=FOAM, hint_text_color=MUTED, cursor_color=MINT,
                         padding=(dp(12), dp(12)), font_size=sp(14))

    @staticmethod
    def field(title, field):
        wrap = BoxLayout(orientation="vertical", spacing=dp(4))
        wrap.add_widget(label(title, size=11, color=MUTED, size_hint_y=None, height=dp(19)))
        wrap.add_widget(field)
        return wrap

    def save(self, *_):
        name = self.name_input.text.strip() or "Приём пищи"
        try:
            kcal = int(self.kcal_input.text)
            if kcal <= 0:
                raise ValueError
            values = {"name": name, "kcal": kcal,
                      "protein": int(self.protein_input.text or 0),
                      "carbs": int(self.carbs_input.text or 0),
                      "fat": int(self.fat_input.text or 0)}
        except ValueError:
            self.kcal_input.hint_text = "Укажите калории числом больше нуля"
            self.kcal_input.text = ""
            return
        self.on_save(values)
        self.dismiss()


class GoalForm(ModalView):
    def __init__(self, goal, on_save, **kwargs):
        super().__init__(size_hint=(0.88, None), height=dp(245), auto_dismiss=True,
                         background_color=(0, 0, 0, 0), **kwargs)
        panel = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(22))
        rounded_background(panel, CARD, dp(26))
        panel.add_widget(label("Дневная цель", size=20, bold=True, size_hint_y=None,
                               height=dp(38)))
        panel.add_widget(label("Подберите комфортный ориентир на день.", size=12,
                               color=MUTED, size_hint_y=None, height=dp(28)))
        self.input = MealForm.make_input(str(goal), numeric=True)
        panel.add_widget(self.input)
        save = Button(text="Сохранить цель", size_hint_y=None, height=dp(48),
                      background_normal="", background_color=MINT, color=INK, bold=True)
        save.bind(on_release=lambda *_: self.save(on_save))
        panel.add_widget(save)
        self.add_widget(panel)

    def save(self, callback):
        try:
            goal = int(self.input.text)
            if goal < 500 or goal > 10000:
                raise ValueError
        except ValueError:
            self.input.hint_text = "От 500 до 10 000 ккал"
            self.input.text = ""
            return
        callback(goal)
        self.dismiss()

class CalorieApp(App):
    title = "Море калорий"

    def build(self):
        self.data_path = os.path.join(self.user_data_dir, "calorie_diary.json")
        self.data = self.load_data()
        self.today = date.today().isoformat()
        self.data.setdefault("days", {}).setdefault(self.today, [])
        self.goal = int(self.data.get("goal", 2000))

        root = BoxLayout(orientation="vertical", padding=(dp(18), dp(8), dp(18), dp(10)),
                         spacing=dp(4))
        self.paint_background(root)
        root.add_widget(self.header())

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(10), bar_margin=dp(3),
                            bar_color=MINT, bar_inactive_color=(MINT[0], MINT[1], MINT[2], 0.42),
                            scroll_type=["bars", "content"])
        self.content = BoxLayout(orientation="vertical", spacing=dp(14),
                                 size_hint_y=None, padding=(0, dp(8), 0, dp(12)))
        self.content.bind(minimum_height=self.content.setter("height"))
        self.content.add_widget(self.intro())
        self.content.add_widget(self.progress_card())
        self.content.add_widget(self.macro_card())
        self.content.add_widget(self.meals_card())
        self.content.add_widget(self.dishes_card())
        scroll.add_widget(self.content)
        root.add_widget(scroll)

        add = Button(text="+ Добавить еду", size_hint_y=None, height=dp(56),
                     background_normal="", background_color=MINT, color=INK,
                     bold=True, font_size=sp(16))
        add.bind(on_release=lambda *_: MealForm(self.add_meal).open())
        root.add_widget(add)
        self.refresh()
        return root

    def header(self):
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        mark = label("≈", size=28, color=MINT, bold=True, size_hint_x=None, width=dp(32))
        row.add_widget(mark)
        row.add_widget(label("Морской колорийник, доведет вас до взвалнованого состояния", size=13, bold=True, color=FOAM))
        row.add_widget(label(date.today().strftime("%d.%m.%Y"), size=12, color=MUTED,
                             halign="right"))
        return row

    def intro(self):
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(76), spacing=dp(2))
        box.add_widget(label("Твой день у моря", size=24, bold=True, size_hint_y=None,
                             height=dp(42)))
        box.add_widget(label("Маленькие шаги — большая гармония", size=13, color=MUTED,
                             size_hint_y=None, height=dp(28)))
        return box

    def progress_card(self):
        card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(196),
                         padding=dp(16), spacing=dp(12))
        rounded_background(card, CARD)
        self.ring = ProgressRing(size_hint_x=None, width=dp(142))
        center = BoxLayout(orientation="vertical", size_hint=(None, None),
                           size=(dp(105), dp(56)), spacing=0)
        self.ring.add_widget(center)
        center.add_widget(label("0", size=25, bold=True, halign="center"))
        center.add_widget(label("ккал", size=11, color=MUTED, halign="center"))
        self.ring_center = center
        card.add_widget(self.ring)
        details = BoxLayout(orientation="vertical", spacing=dp(6), padding=(0, dp(16), 0, dp(8)))
        details.add_widget(label("СЪЕДЕНО", size=10, color=MUTED, bold=True,
                                 size_hint_y=None, height=dp(20)))
        self.left_label = label("Осталось 2 000 ккал", size=15, bold=True,
                                size_hint_y=None, height=dp(28))
        details.add_widget(self.left_label)
        self.goal_button = Button(text="Цель: 2 000 ккал", size_hint=(None, None),
                                  size=(dp(160), dp(34)), background_normal="",
                                  background_color=CARD_LIGHT, color=MINT, font_size=sp(11))
        self.goal_button.bind(on_release=lambda *_: GoalForm(self.goal, self.set_goal).open())
        details.add_widget(self.goal_button)
        details.add_widget(Widget())
        card.add_widget(details)
        Clock.schedule_once(lambda *_: self.position_ring_center(), 0)
        self.ring.bind(pos=lambda *_: self.position_ring_center(),
                       size=lambda *_: self.position_ring_center())
        return card

    def position_ring_center(self):
        if hasattr(self, "ring") and hasattr(self, "ring_center"):
            self.ring_center.center = self.ring.center

    def macro_card(self):
        card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(108),
                         padding=(dp(16), dp(11)), spacing=dp(7))
        rounded_background(card, CARD)
        card.add_widget(label("ПИТАТЕЛЬНЫЙ БАЛАНС", size=10, bold=True, color=MUTED,
                              size_hint_y=None, height=dp(20)))
        row = BoxLayout(spacing=dp(10))
        self.macro_labels = []
        for title, tint in (("Белки", MINT), ("Углеводы", CORAL), ("Жиры", FOAM)):
            col = BoxLayout(orientation="vertical", spacing=0)
            value = label("0 г", size=16, bold=True, color=tint)
            col.add_widget(value)
            col.add_widget(label(title, size=10, color=MUTED))
            row.add_widget(col)
            self.macro_labels.append(value)
        card.add_widget(row)
        return card

    def meals_card(self):
        card = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        rounded_background(card, CARD)
        heading = BoxLayout(size_hint_y=None, height=dp(30))
        heading.add_widget(label("Сегодня в меню", size=16, bold=True))
        self.meal_count = label("0 записей", size=11, color=MUTED, halign="right")
        heading.add_widget(self.meal_count)
        card.add_widget(heading)
        self.meal_rows = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.meal_rows.bind(minimum_height=self.meal_rows.setter("height"))
        card.add_widget(self.meal_rows)
        self.empty_hint = label("Пока тихо. Добавь первый приём пищи", size=12,
                                color=MUTED, size_hint_y=None, height=dp(52), halign="center")
        card.add_widget(self.empty_hint)
        self.meals_card_widget = card
        self.meal_rows.bind(height=lambda *_: self.update_meals_card_height())
        self.empty_hint.bind(height=lambda *_: self.update_meals_card_height())
        return card

    def paint_background(self, root):
        def redraw(*_):
            x, y = root.pos
            width, height = root.size
            root.canvas.before.clear()
            with root.canvas.before:
                Color(*DEEP)
                RoundedRectangle(pos=(x, y), size=(width, height), radius=[0])
                # Short, low-contrast streaks leave most of the background calm.
                Color(MINT[0], MINT[1], MINT[2], 0.075)
                Line(points=[x + width * 0.66, y + height * 0.93,
                             x + width * 0.91, y + height * 0.80], width=dp(20))
                Line(points=[x + width * 0.72, y + height * 0.96,
                             x + width * 0.98, y + height * 0.83], width=dp(7))
                Color(0.25, 0.64, 0.70, 0.08)
                Line(points=[x + width * 0.02, y + height * 0.28,
                             x + width * 0.24, y + height * 0.16], width=dp(12))
                Line(points=[x + width * 0.06, y + height * 0.24,
                             x + width * 0.18, y + height * 0.17], width=dp(5))
                Color(MINT[0], MINT[1], MINT[2], 0.055)
                Line(points=[x + width * 0.78, y + height * 0.50,
                             x + width * 0.99, y + height * 0.60], width=dp(10))

        redraw()
        root.bind(pos=redraw, size=redraw)

    def update_meals_card_height(self):
        if hasattr(self, "meals_card_widget"):
            # 28dp padding + 30dp title + two 10dp gaps.
            self.meals_card_widget.height = (dp(78) + self.meal_rows.height
                                             + self.empty_hint.height)

    def dishes_card(self):
        card = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(16), spacing=dp(8))
        rounded_background(card, CARD)
        card.add_widget(label("Калорийность популярных блюд", size=15, bold=True,
                              size_hint_y=None, height=dp(30)))
        card.add_widget(label("Примерно на 100 г · зависит от рецепта", size=11,
                              color=MUTED, size_hint_y=None, height=dp(26)))
        self.dish_rows = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        self.dish_rows.bind(minimum_height=self.dish_rows.setter("height"))
        for name, kcal in Bludo:
            self.dish_rows.add_widget(DishRow(name, kcal))
        card.add_widget(self.dish_rows)
        card.height = dp(30 + 26 + 32 + 16) + self.dish_rows.height
        self.dish_rows.bind(height=lambda _rows, height: setattr(
            card, "height", dp(30 + 26 + 32 + 16) + height))
        return card

    def entries(self):
        return self.data["days"].setdefault(self.today, [])

    def refresh(self):
        meals = self.entries()
        total = sum(int(meal.get("kcal", 0)) for meal in meals)
        ratio = total / max(self.goal, 1)
        self.ring.progress = ratio
        self.ring_center.children[1].text = f"{total:,}".replace(",", " ")
        remaining = max(self.goal - total, 0)
        self.left_label.text = f"Осталось {remaining:,} ккал".replace(",", " ") if remaining else "Цель достигнута!"
        self.goal_button.text = f"Цель: {self.goal:,} ккал ".replace(",", " ")
        self.macro_labels[0].text = f"{sum(int(m.get('protein', 0)) for m in meals)} г"
        self.macro_labels[1].text = f"{sum(int(m.get('carbs', 0)) for m in meals)} г"
        self.macro_labels[2].text = f"{sum(int(m.get('fat', 0)) for m in meals)} г"
        self.meal_rows.clear_widgets()
        for index, meal in enumerate(meals):
            self.meal_rows.add_widget(MealRow(meal, lambda i=index: self.delete_meal(i)))
        self.empty_hint.opacity = 1 if not meals else 0
        self.empty_hint.disabled = bool(meals)
        self.empty_hint.height = dp(52) if not meals else 0
        self.meal_count.text = f"{len(meals)} записей"
        self.update_meals_card_height()

    def add_meal(self, meal):
        self.entries().append(meal)
        self.persist()
        self.refresh()

    def delete_meal(self, index):
        meals = self.entries()
        if 0 <= index < len(meals):
            meals.pop(index)
            self.persist()
            self.refresh()

    def set_goal(self, goal):
        self.goal = goal
        self.data["goal"] = goal
        self.persist()
        self.refresh()

    def load_data(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as stream:
                saved = json.load(stream)
            if isinstance(saved, dict) and isinstance(saved.get("days", {}), dict):
                return saved
        except (OSError, ValueError, TypeError):
            pass
        return {"goal": 2000, "days": {}}

    def persist(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        temporary = self.data_path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as stream:
            json.dump(self.data, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, self.data_path)


if __name__ == "__main__":
    CalorieApp().run()
