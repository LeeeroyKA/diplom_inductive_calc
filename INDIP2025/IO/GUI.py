import customtkinter as ctk
from IO.zip_window import ZIPWindow
from IO.sip_window import SIPWindow
from IO.pip_window import PIPWindow

class InputWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка внешнего вида - выбор светлой/темной темы системы
        ctk.set_appearance_mode("System")
        # Установка синей цветовой темы для элементов интерфейса
        ctk.set_default_color_theme("blue")

        # Настройка окна - заголовок окна
        self.title("Расчет параметров и характеристик преобразователя")
        # Установка размера окна 800x800 пикселей
        self.geometry("800x800")

        # Создание и размещение элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""

        # 1. Строка для ввода диапазона измерений
        # Создание метки с текстом
        self.range_label = ctk.CTkLabel(
            self,  # родительский элемент - главное окно
            text="Диапазон измерений:"  # текст метки
        )
        # Размещение метки в окне с отступами 20px сверху/снизу и 20px слева/справа
        # sticky="w" - выравнивание по левому краю (west)
        self.range_label.pack(pady=20, padx=20, anchor="w")

        # Создание поля для ввода диапазона измерений
        self.range_entry = ctk.CTkEntry(
            self,  # родительский элемент - главное окно
            placeholder_text="Введите диапазон, согласно Вашему заданию"  # текст-подсказка
        )
        # Размещение поля ввода с отступами
        self.range_entry.pack(pady=(0, 20), padx=20, fill="x")

        # 2. Строка для ввода допустимой приведенной погрешности
        # Создание метки для погрешности
        self.error_label = ctk.CTkLabel(
            self,
            text="Допустимая приведенная погрешность:"
        )
        # Размещение метки с выравниванием по левому краю
        self.error_label.pack(pady=20, padx=20, anchor="w")

        # Создание поля для ввода погрешности
        self.error_entry = ctk.CTkEntry(
            self,
            placeholder_text="Введите погрешность в %"
        )
        # Размещение поля ввода
        self.error_entry.pack(pady=(0, 20), padx=20, fill="x")

        # 3. Радиокнопки для выбора типа датчика
        # Создание метки для выбора датчика
        self.sensor_label = ctk.CTkLabel(
            self,
            text="Тип датчика:"
        )
        # Размещение метки
        self.sensor_label.pack(pady=20, padx=20, anchor="w")

        # Создание фрейма для группировки радиокнопок датчиков
        self.sensor_frame = ctk.CTkFrame(self)
        # Размещение фрейма с отступами
        self.sensor_frame.pack(pady=(0, 20), padx=20, fill="x")

        # Переменная для хранения выбранного датчика
        self.sensor_var = ctk.StringVar(value="ДСИП")

        # Создание радиокнопки для ДСИП
        self.sensor_dsip = ctk.CTkRadioButton(
            self.sensor_frame,  # родитель - фрейм датчиков
            text="ДСИП",  # текст кнопки
            variable=self.sensor_var,  # связь с переменной
            value="ДСИП"  # значение при выборе
        )
        # Размещение радиокнопки в фрейме с отступом слева
        self.sensor_dsip.pack(side="left", padx=20, pady=10)

        # Создание радиокнопки для ДЗИП
        self.sensor_dzip = ctk.CTkRadioButton(
            self.sensor_frame,
            text="ДЗИП",
            variable=self.sensor_var,
            value="ДЗИП"
        )
        # Размещение радиокнопки в фрейме
        self.sensor_dzip.pack(side="left", padx=20, pady=10)

        # Создание радиокнопки для ДПИП
        self.sensor_dpip = ctk.CTkRadioButton(
            self.sensor_frame,
            text="ДПИП",
            variable=self.sensor_var,
            value="ДПИП"
        )
        # Размещение радиокнопки в фрейме
        self.sensor_dpip.pack(side="left", padx=20, pady=10)

        # 4. Радиокнопки для выбора типа схемы включения
        # Создание метки для выбора схемы
        self.scheme_label = ctk.CTkLabel(
            self,
            text="Тип схемы включения преобразователя:"
        )
        # Размещение метки
        self.scheme_label.pack(pady=20, padx=20, anchor="w")

        # Создание фрейма для группировки радиокнопок схем
        self.scheme_frame = ctk.CTkFrame(self)
        # Размещение фрейма с отступами
        self.scheme_frame.pack(pady=(0, 20), padx=20, fill="x")

        # Переменная для хранения выбранной схемы
        self.scheme_var = ctk.StringVar(value="ПРСМ")

        # Создание радиокнопки для ПРСМ
        self.scheme_prsm = ctk.CTkRadioButton(
            self.scheme_frame,  # родитель - фрейм схем
            text="ПРСМ",  # текст кнопки
            variable=self.scheme_var,  # связь с переменной
            value="ПРСМ"  # значение при выборе
        )
        # Размещение радиокнопки в фрейме с отступом слева
        self.scheme_prsm.pack(side="left", padx=20, pady=10)

        # Создание радиокнопки для ПОСМ
        self.scheme_posm = ctk.CTkRadioButton(
            self.scheme_frame,
            text="ПОСМ",
            variable=self.scheme_var,
            value="ПОСМ"
        )
        # Размещение радиокнопки в фрейме
        self.scheme_posm.pack(side="left", padx=20, pady=10)

        # 5. Кнопка "Начать расчет"
        self.calculate_button = ctk.CTkButton(
            self,
            text="Начать расчет",  # текст на кнопке
            command=self.start_calculation  # функция, вызываемая при нажатии
        )
        # Размещение кнопки с большими отступами сверху
        self.calculate_button.pack(pady=40)

    def start_calculation(self):
        """Функция, вызываемая при нажатии кнопки 'Начать расчет'"""
        # Получение введенных значений
        xv = self.range_entry.get()
        d_zT_min = self.error_entry.get()
        selected_sensor = self.sensor_var.get()
        selected_scheme = self.scheme_var.get()

        # Проверка заполнения обязательных полей
        if not xv or not d_zT_min:
            # Создание окна с ошибкой
            error_window = ctk.CTkToplevel(self)
            error_window.title("Ошибка")
            error_window.geometry("300x150")

            error_label = ctk.CTkLabel(error_window, text="Пожалуйста, заполните все поля!")
            error_label.pack(pady=20)

            ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
            ok_button.pack(pady=10)
            return

        # Сохранение результатов
        params = {
            'xv': float(xv),
            'd_zT_min': float(d_zT_min),
            'selected_sensor': selected_sensor,
            'selected_scheme': selected_scheme
        }

        print(f"Получены параметры из GUI:")
        print(f"Диапазон: {xv}")
        print(f"Погрешность: {d_zT_min}%")
        print(f"Датчик: {selected_sensor}")
        print(f"Схема: {selected_scheme}")

        # Скрываем главное окно
        self.withdraw()

        # Создаем окно результатов в зависимости от выбора датчика
        if selected_sensor == "ДЗИП":
            result_window = ZIPWindow(self, params)
        elif selected_sensor == "ДПИП":
            result_window = SIPWindow(self, params)
        else:
            result_window = PIPWindow(self, params)

        # Устанавливаем обработчик закрытия дочернего окна
        result_window.protocol("WM_DELETE_WINDOW", lambda: self.on_result_window_close(result_window))

    def on_result_window_close(self, result_window):
        """Обработчик закрытия окна результатов"""
        result_window.destroy()
        self.destroy()  # Полностью закрываем приложение