from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime


class KalymCalcApp(App):
    def build(self):
        # Главный макет с ScrollView
        main_layout = BoxLayout(orientation='vertical')

        # ScrollView для прокрутки на маленьких экранах
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical',
                            padding=(dp(20), dp(15)),
                            spacing=dp(15),
                            size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Увеличиваем высоту всех элементов для мобильных устройств
        element_height = dp(50)
        button_height = dp(60)
        label_height = dp(40)

        # Заголовок
        content.add_widget(Label(
            text='Калькулятор заявок',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=label_height * 1.5
        ))

        # Поля ввода с фиксированной высотой
        self.hourly_rate = self.create_input(
            'Рублей в час (дневная смена)',
            input_type='number',
            height=element_height
        )
        self.change_time = self.create_input(
            'Время изменения ставки (например 18:00)',
            height=element_height
        )
        self.new_hourly_rate = self.create_input(
            'Новая ставка после изменения (например 500)',
            input_type='number',
            height=element_height
        )
        self.min_hours = self.create_input(
            'Минималка (часы)',
            input_type='number',
            height=element_height
        )
        self.hours_worked = self.create_input(
            'Отработано часов или время (например 08:00-17:00)',
            height=element_height
        )
        self.floors = self.create_input(
            'Доп. услуги (этажи, сборка и т.д.) (Кол-во)',
            input_type='number',
            height=element_height
        )
        self.pay_per_floor = self.create_input(
            'Оплата доп. услуг',
            input_type='number',
            height=element_height
        )

        # Добавляем все поля
        content.add_widget(self.hourly_rate)
        content.add_widget(self.change_time)
        content.add_widget(self.new_hourly_rate)
        content.add_widget(self.min_hours)
        content.add_widget(self.hours_worked)
        content.add_widget(self.floors)
        content.add_widget(self.pay_per_floor)

        # Кнопки
        btn_calculate = Button(
            text='Рассчитать',
            size_hint_y=None,
            height=button_height,
            background_color=(0, 0.7, 0, 1)
        )
        btn_calculate.bind(on_press=self.calculate)

        btn_cancel = Button(
            text='Отмена',
            size_hint_y=None,
            height=button_height,
            background_color=(1, 0, 0, 1)
        )
        btn_cancel.bind(on_press=self.clear_inputs)

        content.add_widget(btn_calculate)
        content.add_widget(btn_cancel)

        # Результат
        self.result_label = Label(
            text='Итог: 0 руб',
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=label_height
        )
        content.add_widget(self.result_label)

        # Подсказка
        content.add_widget(Label(
            text='(Если поле не заполнено, то система подставит в него 0)',
            font_size=dp(14),
            size_hint_y=None,
            height=label_height
        ))

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        return main_layout

    def create_input(self, hint, input_type='text', height=50):
        """Создает текстовое поле с настройками"""
        return TextInput(
            hint_text=hint,
            input_type=input_type,
            size_hint_y=None,
            height=height,
            multiline=False,
            padding=[dp(10), dp(15), dp(10), dp(15)]
        )

    # Остальные методы (calculate, get_value, get_hours_worked, parse_time, clear_inputs)
    # остаются без изменений, как в вашем исходном коде
    def calculate(self, instance):
        try:
            hourly_rate = self.get_value(self.hourly_rate.text, 0)
            min_hours = self.get_value(self.min_hours.text, 0)
            floors = self.get_value(self.floors.text, 0)
            pay_per_floor = self.get_value(self.pay_per_floor.text, 0)
            change_time = self.parse_time(
                self.change_time.text.strip()) if self.change_time.text.strip() else datetime.strptime("00:00", "%H:%M")
            new_hourly_rate = self.get_value(self.new_hourly_rate.text, hourly_rate)
            hours_worked = self.get_hours_worked(self.hours_worked.text)

            if hours_worked < min_hours:
                hours_worked = min_hours

            current_time = datetime.now().time()
            if current_time >= change_time.time():
                hourly_rate = new_hourly_rate

            total_pay = int(hourly_rate * hours_worked + floors * pay_per_floor)
            self.result_label.text = f"Итог: {total_pay} руб"

        except ValueError:
            self.result_label.text = "Ошибка! Проверь ввод чисел"

    def get_value(self, text, default_value):
        try:
            if text.strip() == '':
                return default_value
            return float(text.strip())
        except ValueError:
            return default_value

    def get_hours_worked(self, input_text):
        if '-' in input_text:
            start_time, end_time = input_text.split('-')
            start_time = self.parse_time(start_time.strip())
            end_time = self.parse_time(end_time.strip())
            worked_hours = (end_time - start_time).seconds / 3600
            return worked_hours
        else:
            return float(input_text.strip()) if input_text.strip() else 0

    def parse_time(self, time_str):
        try:
            if len(time_str) == 2:
                time_str = f"{time_str}:00"
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            raise ValueError("Ошибка! Неверный формат времени.")

    def clear_inputs(self, instance):
        self.hourly_rate.text = ''
        self.min_hours.text = ''
        self.hours_worked.text = ''
        self.floors.text = ''
        self.pay_per_floor.text = ''
        self.change_time.text = ''
        self.new_hourly_rate.text = ''
        self.result_label.text = 'Итог: 0 руб'


KalymCalcApp().run()
