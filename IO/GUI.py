import customtkinter as ctk
from IO.zip_window import ZIPWindow
from IO.sip_window import SIPWindow
from IO.pip_window import PIPWindow


class InputWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка темы по умолчанию
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Настройка окна
        self.title("Расчет параметров и характеристик преобразователя")
        self.geometry("800x800")

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""

        # Заголовок
        title_label = ctk.CTkLabel(
            self,
            text="Расчет параметров преобразователей",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)

        # Панель управления темой
        self.create_theme_selector()

        # Параметры ввода
        self.create_input_fields()

        # Кнопка расчета
        self.create_calculate_button()

    def create_theme_selector(self):
        """Создание переключателя темы"""
        theme_frame = ctk.CTkFrame(self)
        theme_frame.pack(pady=10, padx=20, fill="x")

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Тема интерфейса:",
            font=("Arial", 14, "bold")
        )
        theme_label.pack(side="left", padx=10, pady=10)

        self.theme_var = ctk.StringVar(value="System")

        themes = [
            ("Светлая", "Light"),
            ("Темная", "Dark"),
            ("Системная", "System")
        ]

        for text, value in themes:
            radio = ctk.CTkRadioButton(
                theme_frame,
                text=text,
                variable=self.theme_var,
                value=value,
                command=self.change_theme
            )
            radio.pack(side="left", padx=10, pady=10)

    def create_input_fields(self):
        """Создание полей ввода параметров"""
        # Диапазон измерений
        self.range_entry = self.create_labeled_entry(
            "Диапазон измерений:",
            "Введите диапазон, согласно Вашему заданию"
        )

        # Погрешность
        self.error_entry = self.create_labeled_entry(
            "Допустимая приведенная погрешность:",
            "Введите погрешность в %"
        )

        # Тип датчика
        self.create_sensor_selector()

        # Схема включения
        self.create_scheme_selector()

    def create_labeled_entry(self, label_text, placeholder):
        """Создание метки и поля ввода"""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Arial", 14)
        )
        label.pack(anchor="w", padx=10, pady=(10, 5))

        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            height=35
        )
        entry.pack(fill="x", padx=10, pady=(0, 10))

        return entry

    def create_sensor_selector(self):
        """Создание выбора типа датчика"""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        label = ctk.CTkLabel(
            frame,
            text="Тип датчика:",
            font=("Arial", 14)
        )
        label.pack(anchor="w", padx=10, pady=(10, 5))

        sensor_frame = ctk.CTkFrame(frame)
        sensor_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.sensor_var = ctk.StringVar(value="ДЗИП")

        sensors = [
            ("ДЗИП", "ДЗИП"),
            ("ДСИП", "ДСИП"),
            ("ДПИП", "ДПИП")
        ]

        for text, value in sensors:
            radio = ctk.CTkRadioButton(
                sensor_frame,
                text=text,
                variable=self.sensor_var,
                value=value
            )
            radio.pack(side="left", padx=20, pady=10)

    def create_scheme_selector(self):
        """Создание выбора схемы включения"""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        label = ctk.CTkLabel(
            frame,
            text="Тип схемы включения преобразователя:",
            font=("Arial", 14)
        )
        label.pack(anchor="w", padx=10, pady=(10, 5))

        scheme_frame = ctk.CTkFrame(frame)
        scheme_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.scheme_var = ctk.StringVar(value="ПРСМ")

        schemes = [
            ("ПРСМ", "ПРСМ"),
            ("ПОСМ", "ПОСМ")
        ]

        for text, value in schemes:
            radio = ctk.CTkRadioButton(
                scheme_frame,
                text=text,
                variable=self.scheme_var,
                value=value
            )
            radio.pack(side="left", padx=20, pady=10)

    def create_calculate_button(self):
        """Создание кнопки расчета"""
        self.calculate_button = ctk.CTkButton(
            self,
            text="Начать расчет",
            command=self.start_calculation,
            height=40,
            font=("Arial", 16, "bold")
        )
        self.calculate_button.pack(pady=30)

    def change_theme(self):
        """Изменение темы интерфейса"""
        ctk.set_appearance_mode(self.theme_var.get())

    def start_calculation(self):
        """Запуск расчета"""
        # Получение введенных значений
        xv = self.range_entry.get()
        d_zT_min = self.error_entry.get()
        selected_sensor = self.sensor_var.get()
        selected_scheme = self.scheme_var.get()

        # Проверка заполнения полей
        if not xv or not d_zT_min:
            self.show_error("Пожалуйста, заполните все поля!")
            return

        # Проверка числовых значений
        try:
            xv_val = float(xv)
            d_zT_min_val = float(d_zT_min)
        except ValueError:
            self.show_error("Пожалуйста, введите корректные числовые значения!")
            return

        # Сохранение параметров
        params = {
            'xv': xv_val,
            'd_zT_min': d_zT_min_val,
            'selected_sensor': selected_sensor,
            'selected_scheme': selected_scheme
        }

        print(f"Параметры расчета:")
        print(f"Диапазон: {xv} мм")
        print(f"Погрешность: {d_zT_min}%")
        print(f"Датчик: {selected_sensor}")
        print(f"Схема: {selected_scheme}")

        # Скрытие главного окна
        self.withdraw()

        # Создание окна результатов
        if selected_sensor == "ДЗИП":
            result_window = ZIPWindow(self, params)
        elif selected_sensor == "ДПИП":
            result_window = SIPWindow(self, params)
        else:
            result_window = PIPWindow(self, params)

        # Обработчик закрытия дочернего окна
        result_window.protocol("WM_DELETE_WINDOW",
                               lambda: self.on_result_window_close(result_window))

    def show_error(self, message):
        """Показать окно ошибки"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Ошибка")
        error_window.geometry("400x150")
        error_window.transient(self)
        error_window.grab_set()

        error_label = ctk.CTkLabel(error_window, text=message, font=("Arial", 14))
        error_label.pack(pady=20)

        ok_button = ctk.CTkButton(error_window, text="OK",
                                  command=error_window.destroy)
        ok_button.pack(pady=10)

    def on_result_window_close(self, result_window):
        """Обработчик закрытия окна результатов"""
        result_window.destroy()
        self.destroy()