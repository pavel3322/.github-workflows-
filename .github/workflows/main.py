from kivy.app import App
from kivy.graphics.cgl_backend.cgl_gl import init_backend
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle

store = JsonStore('tournament_settings.json')

class ImageButton(ButtonBehavior, Image):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_running = False
        self.current_time = 0
        self.level = 1
        self.current_level = "1"
        self.levels = [1, 21]
        self.timer_seconds = 0
        self.current_blinds = (0, 0)
        self.current_ante = 0

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)

        self.bind(size=self.update_bg, pos=self.update_bg)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

        float_layout = FloatLayout()

        layout = BoxLayout(orientation='vertical')

        self.timer_button = ImageButton(source="1.png", size_hint=(None, None), size=(80, 80),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.75}, on_press=self.toggle_timer)
        float_layout.add_widget(self.timer_button)

        self.level_label = Label(text="Уровень: 1", font_size=30, color=(0, 0, 0, 1))
        layout.add_widget(self.level_label)

        self.blind_label = Label(text="Блайнды: 0 / 0", font_size=30, color=(0, 0, 0, 1))
        layout.add_widget(self.blind_label)

        self.ante_label = Label(text="Анте: 0", font_size=30, color=(0, 0, 0, 1))
        layout.add_widget(self.ante_label)

        self.timer_label = Label(text="00:00", font_size=40, color=(0, 0, 0, 1))
        layout.add_widget(self.timer_label)

        self.next_level_button = ImageButton(source="right.jpg", size_hint=(None, None),
                                            size=(70,70), pos_hint={"center_x": 0.75, "y": 0.4},  on_press=self.next_level)
        float_layout.add_widget(self.next_level_button)

        self.prev_level_button = ImageButton(source="left.jpg", size_hint=(None, None), size=(70,70),
                                             pos_hint={"center_x": 0.25, "y": 0.4},  on_press=self.prev_level)
        float_layout.add_widget(self.prev_level_button)

        self.settings_button = ImageButton(source="settings.png",size_hint=(None, None),
                                            size=(50,70), pos_hint={"x": 0.93, "y": 4.35}, on_press=self.open_settings)
        float_layout.add_widget(self.settings_button)

        self.add_widget(layout)
        self.load_settings()
        layout.add_widget(float_layout)

    def toggle_timer(self, instance):
        if self.timer_running:
            self.timer_running = False
            Clock.unschedule(self.update_timer)
            self.timer_button.source = "1.png"
        else:
            self.timer_running = True
            Clock.schedule_interval(self.update_timer, 1)
            self.timer_button.source = "2.png"

    def update_timer(self, dt):
        if self.timer_running:
            if self.current_time >= self.timer_seconds:
                self.next_level()
            else:
                self.current_time += 1
                minutes = self.current_time // 60
                seconds = self.current_time % 60
                self.timer_label.text = f"{minutes:02}:{seconds:02}"

    def next_level(self, instance=None):
        self.load_levels()
        if self.current_level not in self.levels:
            print(f"Ошибка: уровень {self.current_level} отсутствует в списке!")
            return

        current_index = self.levels.index(self.current_level)
        if current_index < len(self.levels) - 1:
            self.current_level = self.levels[current_index + 1]
            self.load_level_settings()
        else:
            print("Это последний уровень")

    def load_levels(self):
        if store.exists("settings"):
            self.levels = list(map(str, store.get('settings').get('levels', {}).keys()))
        else:
            self.levels = []

    def prev_level(self, instance=None):
        self.load_levels()
        if self.current_level not in self.levels:
            print(f"Ошибка: уровень {self.current_level} отсутствует в списке!")
            return

        current_index = self.levels.index(self.current_level)
        if current_index > 0:
            self.current_level = self.levels[current_index - 1]
            self.load_level_settings()
        else:
            print("Это первый уровень")

    def load_level_settings(self):
        if not store.exists('settings'):
            print("Ошибка: настройки не найдены!")
            return

        settings = store.get('settings').get('levels', {})
        self.levels = list(settings.keys())
        if self.current_level not in settings:
            print(f"Ошибка: нет настроек для уровня {self.current_level}")
            return

        try:
            self.current_blinds = (
                settings[self.current_level]['small_blind'],
                settings[self.current_level]['big_blind']
            )
            self.current_ante = settings[self.current_level]['ante']
            self.timer_seconds = int(settings[self.current_level]['time']) * 60
            self.current_time = 0
            self.timer_running = True
            self.update_display()
            print(f"Загружены настройки для уровня {self.current_level}")
        except (KeyError, ValueError) as e:
            print(f"Ошибка загрузки настроек уровня {self.current_level}: {e}")

    def update_display(self):
        self.timer_label.text = f"{self.timer_seconds // 60:02}:{self.timer_seconds % 60:02d}"
        self.level_label.text = f"Уровень: {self.current_level}"
        self.blind_label.text = f"Блайнды: {self.current_blinds[0]}/{self.current_blinds[1]}"
        self.ante_label.text = f"Анте: {self.current_ante}"

    def update_level_display(self):
        self.level_label.text = f"Уровень: {self.level}"
        settings = store.get('settings').get('levels', {})
        blinds = f"{settings.get(str(self.level), {}).get('small_blind', '0')} / {settings.get(str(self.level), {}).get('big_blind', '0')}"
        ante = settings.get(str(self.level), {}).get('ante', '0')
        self.blind_label.text = f"Блайнды: {blinds}"
        self.ante_label.text = f"Анте: {ante}"

    def open_settings(self, instance):
        self.manager.current = 'settings'

    def load_settings(self):
        if store.exists('settings'):
            self.update_level_display()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.level_spinner = Spinner(
            text="Выберите уровень",
            values=[str(i) for i in range(1, 21)],
        )
        self.level_spinner.bind(text=self.load_settings)
        layout.add_widget(self.level_spinner)

        self.blind_small_input = TextInput(hint_text="Малый блайнд", multiline=False)
        layout.add_widget(self.blind_small_input)

        self.blind_big_input = TextInput(hint_text="Большой блайнд", multiline=False)
        layout.add_widget(self.blind_big_input)

        self.ante_input = TextInput(hint_text="Анте", multiline=False)
        layout.add_widget(self.ante_input)

        self.time_input = TextInput(hint_text="Время уровня (1-60 мин)", multiline=False)
        layout.add_widget(self.time_input)

        save_button = Button(text="Сохранить", on_press=self.save_settings)
        layout.add_widget(save_button)

        back_button = Button(text="Назад", on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def save_settings(self, instance):
        level = self.level_spinner.text

        if not self.time_input.text.isdigit() or not (1 <= int(self.time_input.text) <= 60):
            print("Ошибка: Время должно быть от 1 до 60 минут")
            return

        if not store.exists('settings'):
            store.put('settings', levels={})

        settings = store.get('settings')
        if 'levels' not in settings:
            settings['levels'] = {}

        settings['levels'][level] = {
            'small_blind': self.blind_small_input.text,
            'big_blind': self.blind_big_input.text,
            'ante': self.ante_input.text,
            'time': self.time_input.text
        }

        store.put('settings', levels=settings['levels'])
        print(f"Настройки сохранены для уровня {level}")

    def load_levels(self):
        self.levels = sorted(map(str, store.get('settings').get('levels', {}).keys()), key=int)

    def load_settings(self, spinner, level):
        if store.exists('settings'):
            settings = store.get('settings').get('levels', {})
            if level in settings:
                self.blind_small_input.text = settings[level]['small_blind']
                self.blind_big_input.text = settings[level]['big_blind']
                self.ante_input.text = settings[level]['ante']
                self.time_input.text = settings[level]['time']
                print(f"Настройки загружены для уровня {level}")
            else:
                self.blind_small_input.text = ""
                self.blind_big_input.text = ""
                self.ante_input.text = ""
                self.time_input.text = ""

    def go_back(self, instance):
        self.manager.current = 'main'


class PokerTimerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.current = 'main'
        return sm

if __name__ == '__main__':
    PokerTimerApp().run()
