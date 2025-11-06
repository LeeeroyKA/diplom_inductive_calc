import customtkinter as ctk
from models.sensor_zip import ZIPSensor


class ZIPWindow(ctk.CTkToplevel):
    def __init__(self, parent, params):
        super().__init__()
        self.title("ДЗИП - Результаты расчета")
        self.geometry("1400x800")
        self.params = params
        self.sensor = None
        self.calculation_results = None

        # Инициализация параметров из main.py
        self.init_parameters()

        # Создаем сетку - теперь 2 колонки, 1 строка
        self.grid_columnconfigure(0, weight=1)  # Левая колонка (схема + параметры)
        self.grid_columnconfigure(1, weight=2)  # Правая колонка (результаты) - шире
        self.grid_rowconfigure(0, weight=1)  # Единственная строка

        self.create_widgets()

    def init_parameters(self):
        """Инициализация всех параметров из main.py"""
        # Параметры из GUI
        self.xv = self.params['xv']
        self.d_zT_min = self.params['d_zT_min']
        self.selected_sensor = self.params['selected_sensor']
        self.selected_scheme = self.params['selected_scheme']

        # Фиксированные параметры
        self.eta_max = 5
        self.x = 0.003
        self.K_kp = 1
        self.p_n = 17.5 * 10 ** -6  # Удельное сопротивление меди
        self.mu_c = 3000
        self.mu_0 = 4 * 3.141592653589793 * 10 ** -7  # 4 * np.pi * 10 ** -7 (исправлено)
        self.z0 = 1000
        self.z_0_eta = 2000
        # Остальные параметры будут вводиться пользователем

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # 1. Левая панель - объединяем схему и параметры в ScrollableFrame
        self.left_frame = ctk.CTkScrollableFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 1.1 Верхняя часть левой панели - Схема
        self.scheme_frame = ctk.CTkFrame(self.left_frame)
        self.scheme_frame.pack(fill="x", padx=5, pady=5)

        scheme_label = ctk.CTkLabel(self.scheme_frame, text="Схема ДЗИП", font=("Arial", 16, "bold"))
        scheme_label.pack(pady=10)

        scheme_info = ctk.CTkLabel(self.scheme_frame,
                                   text=f"Тип датчика: {self.selected_sensor}\n"
                                        f"Схема включения: {self.selected_scheme}\n"
                                        f"Диапазон: {self.xv} мм\n"
                                        f"Погрешность: {self.d_zT_min}%",
                                   font=("Arial", 12),
                                   justify="left")
        scheme_info.pack(pady=10)

        # Заглушка для изображения схемы
        scheme_placeholder = ctk.CTkLabel(self.scheme_frame, text="[Изображение схемы ДЗИП]",
                                          font=("Arial", 12), fg_color="gray", corner_radius=5,
                                          height=150)
        scheme_placeholder.pack(fill="x", padx=20, pady=20)

        # 1.2 Нижняя часть левой панели - Параметры ввода
        self.input_frame = ctk.CTkFrame(self.left_frame)
        self.input_frame.pack(fill="x", padx=5, pady=5)

        input_label = ctk.CTkLabel(self.input_frame, text="Параметры расчета", font=("Arial", 14, "bold"))
        input_label.pack(pady=5)

        self.create_input_content()

        # 2. Правая панель - Результаты (теперь занимает всю высоту)
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        results_label = ctk.CTkLabel(self.results_frame, text="Результаты расчета", font=("Arial", 16, "bold"))
        results_label.pack(pady=10)

        self.create_results_content()

    def create_input_content(self):
        """Создание содержимого для панели ввода параметров"""
        # Основные геометрические параметры (пустые по умолчанию)
        geometric_params = [
            ("Внешний диаметр D1, мм:", "D1"),
            ("Внешний диаметр D2, мм:", "D2"),
            ("Диаметр отв. d1, мм:", "d1"),
            ("Диаметр отв. d2, мм:", "d2"),
            ("Высота катушки h1, мм:", "h1"),
            ("Высота сердечника h2, мм:", "h2"),
            ("Толщина якоря h3, мм:", "h3"),
            ("Начальный зазор l0, мм:", "l0")
        ]

        # Электрические параметры (пустые по умолчанию)
        electrical_params = [
            ("Диаметр провода d_n, мм:", "d_n"),
            ("Уд. сопр. меди p_n, Ом*мм²/м:", "p_n"),
            ("Магн. прониц. mu_c:", "mu_c"),
            ("Нач. сопр. z0, Ом:", "z0")
        ]

        self.input_entries = {}

        # Геометрические параметры
        geom_label = ctk.CTkLabel(self.input_frame, text="Геометрические параметры:", font=("Arial", 12, "bold"))
        geom_label.pack(pady=(10, 5))

        for label_text, param_name in geometric_params:
            self.create_parameter_row(label_text, param_name, "")

        # Электрические параметры
        elec_label = ctk.CTkLabel(self.input_frame, text="Электрические параметры:", font=("Arial", 12, "bold"))
        elec_label.pack(pady=(20, 5))

        for label_text, param_name in electrical_params:
            self.create_parameter_row(label_text, param_name, "")

        # Фиксированные параметры (только для информации)
        fixed_params_label = ctk.CTkLabel(self.input_frame, text="Фиксированные параметры:", font=("Arial", 12, "bold"))
        fixed_params_label.pack(pady=(20, 5))

        fixed_params_text = ctk.CTkLabel(self.input_frame,
                                         text=f"• Магнитная постоянная μ₀: {self.mu_0:.2e} Гн/м\n"
                                              f"• Макс. КПД η_max: {self.eta_max}\n"
                                              f"• Коэф. заполнения K_kp: {self.K_kp}",
                                         font=("Arial", 11),
                                         justify="left")
        fixed_params_text.pack(pady=5)

        # Кнопки
        button_frame = ctk.CTkFrame(self.input_frame)
        button_frame.pack(fill="x", padx=10, pady=20)

        recalc_btn = ctk.CTkButton(button_frame, text="Рассчитать", command=self.recalculate)
        recalc_btn.pack(side="left", padx=5, expand=True)

        clear_btn = ctk.CTkButton(button_frame, text="Очистить", command=self.clear_parameters)
        clear_btn.pack(side="right", padx=5, expand=True)

    def create_parameter_row(self, label_text, param_name, default_value):
        """Создание строки параметра"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.pack(fill="x", padx=10, pady=2)

        label = ctk.CTkLabel(frame, text=label_text, width=180)
        label.pack(side="left", padx=5)

        entry = ctk.CTkEntry(frame, placeholder_text="Введите значение")
        if default_value:
            entry.insert(0, str(default_value))
        entry.pack(side="right", fill="x", expand=True, padx=5)
        self.input_entries[param_name] = entry

    def create_results_content(self):
        """Создание содержимого для панели результатов"""
        self.results_scroll = ctk.CTkScrollableFrame(self.results_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        title_label = ctk.CTkLabel(self.results_scroll, text="РЕЗУЛЬТАТЫ РАСЧЕТА ДЗИП",
                                   font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Разделитель
        separator = ctk.CTkFrame(self.results_scroll, height=2, fg_color="gray")
        separator.pack(fill="x", pady=5)

        # Контейнер для всех результатов
        self.results_container = ctk.CTkFrame(self.results_scroll)
        self.results_container.pack(fill="both", expand=True)

        # Начальное сообщение
        self.initial_message = ctk.CTkLabel(self.results_container,
                                            text="Введите параметры и нажмите 'Рассчитать'\nдля получения результатов",
                                            font=("Arial", 12),
                                            text_color="gray")
        self.initial_message.pack(pady=50)

    def create_result_section(self, section_name, results_dict):
        """Создание секции с результатами и возвращает словарь с метками значений"""
        section_result_labels = {}

        # Заголовок секции
        section_label = ctk.CTkLabel(self.results_container, text=section_name,
                                     font=("Arial", 14, "bold"))
        section_label.pack(anchor="w", pady=(15, 5))

        # Создаем строки для каждого параметра в секции
        for param_name, param_value in results_dict.items():
            frame = ctk.CTkFrame(self.results_container)
            frame.pack(fill="x", padx=5, pady=2)

            label = ctk.CTkLabel(frame, text=param_name, width=300, anchor="w")
            label.pack(side="left", padx=5)

            value_label = ctk.CTkLabel(frame, text=param_value, width=150, anchor="e")
            value_label.pack(side="right", padx=5)

            section_result_labels[param_name] = value_label

        return section_result_labels

    def recalculate(self):
        """Функция пересчета параметров"""
        try:
            # Обновляем параметры из полей ввода
            self.update_parameters_from_input()

            # Создаем датчик с текущими параметрами
            self.sensor = ZIPSensor(
                D1=self.D1, D2=self.D2, d1=self.d1, d2=self.d2,
                h1=self.h1, h2=self.h2, h3=self.h3, l0=self.l0,
                z0=self.z0, d_n=self.d_n, xv=self.xv, d_zT_min=self.d_zT_min,
                eta_max=self.eta_max, x=self.x, K_kp=self.K_kp, p_n=self.p_n,
                mu_0=self.mu_0, mu_c=self.mu_c, z_0_eta=self.z_0_eta
            )

            # Выполняем расчет
            self.calculation_results = self.sensor.calc()

            # Обновляем результаты в интерфейсе
            self.update_results_display()

        except Exception as e:
            self.show_error(f"Ошибка расчета: {str(e)}")

    def update_parameters_from_input(self):
        """Обновление параметров из полей ввода"""
        try:
            # Обновляем основные параметры
            self.D1 = float(self.input_entries['D1'].get())
            self.D2 = float(self.input_entries['D2'].get())
            self.d1 = float(self.input_entries['d1'].get())
            self.d2 = float(self.input_entries['d2'].get())
            self.h1 = float(self.input_entries['h1'].get())
            self.h2 = float(self.input_entries['h2'].get())
            self.h3 = float(self.input_entries['h3'].get())
            self.l0 = float(self.input_entries['l0'].get())
            self.d_n = float(self.input_entries['d_n'].get())
            self.p_n = float(self.input_entries['p_n'].get())
            self.mu_c = float(self.input_entries['mu_c'].get())
            self.z0 = float(self.input_entries['z0'].get())

        except ValueError as e:
            raise ValueError("Пожалуйста, заполните все поля корректными числовыми значениями")

    def update_results_display(self):
        """Обновление отображения результатов"""
        if not self.calculation_results:
            return

        # Очищаем старые результаты
        for widget in self.results_container.winfo_children():
            widget.destroy()

        self.result_labels = {}

        # Группируем результаты по категориям
        geometric_results = {
            "Площадь сечения воздушной части S_B": f"{self.calculation_results.get('S_B', 0):.6f} мм²",
            "Длина сечения сердечника L_cd": f"{self.calculation_results.get('L_cd', 0):.3f} мм",
            "Площадь сечения сердечника S_cd": f"{self.calculation_results.get('S_cd', 0):.6f} мм²",
            "Площадь якоря S_y": f"{self.calculation_results.get('S_y', 0):.6f} мм²",
            "Длина магнитопровода L_c": f"{self.calculation_results.get('L_c', 0):.3f} мм",
            "Площадь сечения магнитопровода S_c": f"{self.calculation_results.get('S_c', 0):.6f} мм²",
            "Площадь окна катушки S_ok": f"{self.calculation_results.get('S_ok', 0):.3f} мм²",
            "Средний радиус катушки R_cp": f"{self.calculation_results.get('R_cp', 0):.3f} мм"
        }

        electrical_results = {
            "Число витков катушки w": f"{self.calculation_results.get('w', 0):.0f}",
            "Сопротивление катушки R_k": f"{self.calculation_results.get('R_k', 0):.3f} Ом",
            "Магнитное сопротивление R_mC": f"{self.calculation_results.get('R_mC', 0):.3e} 1/Гн",
            "Коэффициент чувствительности k_x": f"{self.calculation_results.get('k_x', 0):.6f}",
            "Частота питания f_p": f"{self.calculation_results.get('f_p', 0):.1f} Гц",
            "Начальное сопротивление z_0": f"{self.calculation_results.get('Z_x', 0):.3f} Ом"
        }

        characteristics_results = {
            "Приведенная погрешность gamma": f"{self.calculation_results.get('gamma', 0):.6f}",
            "Максимальная погрешность d_z": f"{self.calculation_results.get('d_z', 0):.6f}",
            "Доля активного сопротивления eta": f"{self.calculation_results.get('eta', 0):.6f}"
        }

        # Создаем секции с результатами
        self.create_result_section("ГЕОМЕТРИЧЕСКИЕ ПАРАМЕТРЫ", geometric_results)
        self.create_result_section("ЭЛЕКТРИЧЕСКИЕ ПАРАМЕТРЫ", electrical_results)
        self.create_result_section("ХАРАКТЕРИСТИКИ", characteristics_results)

    def clear_parameters(self):
        """Очистка всех полей ввода"""
        for entry in self.input_entries.values():
            entry.delete(0, "end")

        # Очищаем результаты
        for widget in self.results_container.winfo_children():
            widget.destroy()

        # Показываем начальное сообщение
        self.initial_message = ctk.CTkLabel(self.results_container,
                                            text="Введите параметры и нажмите 'Рассчитать'\nдля получения результатов",
                                            font=("Arial", 12),
                                            text_color="gray")
        self.initial_message.pack(pady=50)

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        # Очищаем старые результаты
        for widget in self.results_container.winfo_children():
            widget.destroy()

        error_label = ctk.CTkLabel(self.results_container, text=f"ОШИБКА:\n{message}",
                                   font=("Arial", 12), text_color="red")
        error_label.pack(pady=20)