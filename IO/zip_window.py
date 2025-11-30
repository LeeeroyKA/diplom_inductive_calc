import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from models.sensor_zip import ZIPSensor


class ZIPWindow(ctk.CTkToplevel):
    def __init__(self, parent, params=None):
        super().__init__(parent)
        self.title("ДЗИП — Расчёт и схема")
        self.geometry("1400x800")
        self.params = params or {}
        self.sensor = None
        self.calculation_results = None
        self.current_file_path = None

        # Инициализация параметров
        self.init_parameters()

        # Настройка сетки
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Создание виджетов
        self.create_widgets()

    def init_parameters(self):
        """Инициализация параметров по умолчанию"""
        # Основные параметры из родительского окна
        self.xv = self.params.get("xv", 0.0)
        self.d_zT_min = self.params.get("d_zT_min", 0.0)
        self.selected_sensor = self.params.get("selected_sensor", "ДЗИП")
        self.selected_scheme = self.params.get("selected_scheme", "ПРСМ")

        # Общие параметры (будут вводиться пользователем)
        self.eta_max = 5.0
        self.x = 0.003
        self.K_kp = 1.0
        self.p_n = 17.5e-6
        self.mu_c = 3000.0
        self.mu_0 = 4 * 3.141592653589793e-7
        self.z0 = 1000.0

        # Геометрические параметры (пустые по умолчанию)
        self.D1 = 0.0
        self.D2 = 0.0
        self.d1 = 0.0
        self.d2 = 0.0
        self.h1 = 0.0
        self.h2 = 0.0
        self.h3 = 0.0
        self.l0 = 0.0

        # Электрические параметры (пустые по умолчанию)
        self.d_n = 0.0
        self.p_n_user = 0.0
        self.mu_c_user = 0.0
        self.z0_user = 0.0

    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Левая панель - параметры
        self.create_left_panel()

        # Правая панель - схема и результаты
        self.create_right_panel()

    def create_left_panel(self):
        """Создание левой панели с параметрами"""
        self.left_frame = ctk.CTkScrollableFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # Заголовок
        header = ctk.CTkLabel(
            self.left_frame,
            text="ПАРАМЕТРЫ РАСЧЁТА",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=8)

        # Переключатель темы
        self.create_theme_switch()

        # Информация о требованиях
        self.create_requirements_section()

        # Поля ввода
        self.input_entries = {}
        self.input_frames = {}
        self.create_input_sections()

        # Кнопки управления
        self.create_control_buttons()

        # Статус файла
        self.file_status_label = ctk.CTkLabel(
            self.left_frame,
            text="Файл не сохранён",
            text_color="gray"
        )
        self.file_status_label.pack(pady=6)

    def create_requirements_section(self):
        """Создание секции с требованиями из родительского окна"""
        requirements_label = ctk.CTkLabel(
            self.left_frame,
            text="ТРЕБОВАНИЯ К ДАТЧИКУ:",
            font=("Arial", 12, "bold")
        )
        requirements_label.pack(pady=(6, 4), anchor="w")

        requirements_frame = ctk.CTkFrame(self.left_frame)
        requirements_frame.pack(fill="x", padx=6, pady=4)

        # Диапазон измерений
        xv_label = ctk.CTkLabel(
            requirements_frame,
            text=f"Диапазон измерений xv: {self.format_value(self.xv)} мм",
            font=("Arial", 11)
        )
        xv_label.pack(anchor="w", padx=8, pady=2)

        # Погрешность
        d_zT_min_label = ctk.CTkLabel(
            requirements_frame,
            text=f"Мин. погрешность d_zT_min: {self.format_value(self.d_zT_min)} %",
            font=("Arial", 11)
        )
        d_zT_min_label.pack(anchor="w", padx=8, pady=2)

        # Тип датчика и схема
        sensor_label = ctk.CTkLabel(
            requirements_frame,
            text=f"Тип датчика: {self.selected_sensor}",
            font=("Arial", 11)
        )
        sensor_label.pack(anchor="w", padx=8, pady=2)

        scheme_label = ctk.CTkLabel(
            requirements_frame,
            text=f"Схема подключения: {self.selected_scheme}",
            font=("Arial", 11)
        )
        scheme_label.pack(anchor="w", padx=8, pady=2)

    def create_theme_switch(self):
        """Создание переключателя темы"""
        theme_frame = ctk.CTkFrame(self.left_frame)
        theme_frame.pack(fill="x", padx=6, pady=(0, 10))

        theme_label = ctk.CTkLabel(theme_frame, text="Тема:")
        theme_label.pack(side="left", padx=5)

        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())

        theme_light = ctk.CTkRadioButton(
            theme_frame,
            text="Светлая",
            variable=self.theme_var,
            value="Light",
            command=self.change_theme
        )
        theme_light.pack(side="left", padx=2)

        theme_dark = ctk.CTkRadioButton(
            theme_frame,
            text="Темная",
            variable=self.theme_var,
            value="Dark",
            command=self.change_theme
        )
        theme_dark.pack(side="left", padx=2)

    def create_input_sections(self):
        """Создание секций ввода параметров"""
        # Общие параметры
        self.create_common_section()

        # Геометрические параметры
        self.create_geometry_section()

        # Электрические параметры
        self.create_electrical_section()

    def create_common_section(self):
        """Создание секции общих параметров"""
        common_label = ctk.CTkLabel(
            self.left_frame,
            text="Общие параметры:",
            font=("Arial", 12, "bold")
        )
        common_label.pack(pady=(10, 4), anchor="w")

        common_params = [
            ("Макс. КПД eta_max:", "eta_max", "5.0"),
            ("Относит. погрешность x:", "x", "0.003"),
            ("Коэф. использования K_kp:", "K_kp", "1.0"),
            ("Магн. прониц. вакуума mu_0:", "mu_0", "1.256637e-6"),
        ]

        for label_text, name, default in common_params:
            self.create_input_row(label_text, name, default)

    def create_geometry_section(self):
        """Создание секции геометрических параметров"""
        geom_label = ctk.CTkLabel(
            self.left_frame,
            text="Геометрические параметры:",
            font=("Arial", 12, "bold")
        )
        geom_label.pack(pady=(10, 4), anchor="w")

        geom_params = [
            ("Внешний диаметр D1, мм:", "D1", ""),
            ("Внешний диаметр D2, мм:", "D2", ""),
            ("Диаметр отв. d1, мм:", "d1", ""),
            ("Диаметр отв. d2, мм:", "d2", ""),
            ("Высота катушки h1, мм:", "h1", ""),
            ("Высота сердечника h2, мм:", "h2", ""),
            ("Толщина якоря h3, мм:", "h3", ""),
            ("Начальный зазор l0, мм:", "l0", ""),
        ]

        for label_text, name, default in geom_params:
            self.create_input_row(label_text, name, default)

    def create_electrical_section(self):
        """Создание секции электрических параметров"""
        elec_label = ctk.CTkLabel(
            self.left_frame,
            text="Электрические параметры:",
            font=("Arial", 12, "bold")
        )
        elec_label.pack(pady=(10, 4), anchor="w")

        elec_params = [
            ("Диаметр провода d_n, мм:", "d_n", ""),
            ("Уд. сопр. меди p_n, Ом·мм²/м:", "p_n_user", ""),
            ("Магн. прониц. mu_c:", "mu_c_user", ""),
            ("Нач. сопр. z0, Ом:", "z0_user", ""),
        ]

        for label_text, name, default in elec_params:
            self.create_input_row(label_text, name, default)

    def create_input_row(self, label_text, name, default):
        """Создание строки ввода параметра"""
        row = ctk.CTkFrame(self.left_frame)
        row.pack(fill="x", padx=6, pady=2)

        lbl = ctk.CTkLabel(row, text=label_text, width=180)
        lbl.pack(side="left", padx=4)

        frame = ctk.CTkFrame(row, fg_color="transparent")
        frame.pack(side="right", fill="x", expand=True)

        ent = ctk.CTkEntry(frame)
        if default:
            ent.insert(0, default)
        ent.pack(fill="x", padx=4)

        self.input_entries[name] = ent
        self.input_frames[name] = frame

    def create_control_buttons(self):
        """Создание кнопок управления"""
        # Основные кнопки
        btn_frame1 = ctk.CTkFrame(self.left_frame)
        btn_frame1.pack(fill="x", padx=6, pady=(8, 4))
        btn_frame1.grid_columnconfigure(0, weight=1)
        btn_frame1.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame1,
            text="Обновить схему",
            fg_color="#FF8C00",
            command=self.draw_zip_scheme
        ).grid(row=0, column=0, padx=2, sticky="ew")

        ctk.CTkButton(
            btn_frame1,
            text="Рассчитать",
            command=self.recalculate
        ).grid(row=0, column=1, padx=2, sticky="ew")

        # Дополнительные кнопки
        btn_frame2 = ctk.CTkFrame(self.left_frame)
        btn_frame2.pack(fill="x", padx=6, pady=(4, 8))
        btn_frame2.grid_columnconfigure(0, weight=1)
        btn_frame2.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame2,
            text="Очистить",
            command=self.clear_parameters
        ).grid(row=0, column=0, padx=2, sticky="ew")

        ctk.CTkButton(
            btn_frame2,
            text="Печать",
            fg_color="#8B4513",
            command=self.print_results
        ).grid(row=0, column=1, padx=2, sticky="ew")

        # Кнопки файловых операций
        file_frame = ctk.CTkFrame(self.left_frame)
        file_frame.pack(fill="x", padx=6, pady=(10, 0))

        ctk.CTkButton(
            file_frame,
            text="Сохранить расчет",
            fg_color="#2E8B57",
            hover_color="#3CB371",
            command=self.save_calculation
        ).pack(side="left", padx=4, expand=True)

        ctk.CTkButton(
            file_frame,
            text="Загрузить расчет",
            fg_color="#4169E1",
            hover_color="#6495ED",
            command=self.load_calculation
        ).pack(side="right", padx=4, expand=True)

    def create_right_panel(self):
        """Создание правой панели со схемой и результатами"""
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Схема
        self.create_scheme_frame()

        # Результаты расчета
        self.create_results_frame()

    def create_scheme_frame(self):
        """Создание фрейма со схемой"""
        self.scheme_frame = ctk.CTkFrame(self.right_frame)
        self.scheme_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        label = ctk.CTkLabel(
            self.scheme_frame,
            text="Расчётная схема ЗИП",
            font=("Arial", 14, "bold")
        )
        label.pack(pady=4)

        self.create_scheme_canvas()

    def create_results_frame(self):
        """Создание фрейма с результатами"""
        self.results_frame = ctk.CTkFrame(self.right_frame)
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        rlabel = ctk.CTkLabel(
            self.results_frame,
            text="РЕЗУЛЬТАТЫ РАСЧЁТА",
            font=("Arial", 14, "bold")
        )
        rlabel.pack(pady=6)

        self.results_scroll = ctk.CTkScrollableFrame(self.results_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=6, pady=6)

        self.results_container = ctk.CTkFrame(self.results_scroll)
        self.results_container.pack(fill="both", expand=True)

        self.initial_message = ctk.CTkLabel(
            self.results_container,
            text="Введите параметры и нажмите 'Рассчитать'",
            text_color="gray"
        )
        self.initial_message.pack(pady=20)

    def create_scheme_canvas(self):
        """Создание холста для схемы"""
        appearance = ctk.get_appearance_mode()
        facecolor = "white" if appearance.lower().startswith("light") else "#2b2b2b"

        # Возвращаем исходный размер схемы
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=50)
        self.figure.patch.set_facecolor(facecolor)
        self.ax.set_facecolor(facecolor)
        self.ax.set_aspect("equal")

        self.draw_empty_scheme()

        self.canvas = FigureCanvasTkAgg(self.figure, self.scheme_frame)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=6, pady=6)

    def draw_empty_scheme(self):
        """Отрисовка пустой схемы при отсутствии параметров"""
        appearance = ctk.get_appearance_mode()
        if appearance.lower().startswith("dark"):
            bg = "#2b2b2b"
            line_color = "white"
            text_color = "white"
        else:
            bg = "white"
            line_color = "black"
            text_color = "black"

        self.ax.clear()
        self.figure.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.ax.set_aspect("equal")

        # Отображаем сообщение о необходимости ввода параметров
        self.ax.text(0, 0, "Введите параметры и нажмите\n'Обновить схему'",
                     ha='center', va='center', fontsize=14, color=text_color,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor=bg,
                               edgecolor=line_color, linewidth=1))

        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.axis("off")

        if hasattr(self, "canvas"):
            self.canvas.draw()

    def change_theme(self):
        """Изменение темы интерфейса"""
        ctk.set_appearance_mode(self.theme_var.get())
        if any([self.D1, self.D2, self.d1, self.d2, self.h1, self.h2, self.h3, self.l0]):
            self.draw_zip_scheme()
        else:
            self.draw_empty_scheme()

    def format_value(self, value):
        """Форматирование значения с округлением до 3 знаков"""
        if isinstance(value, (int, float)):
            if abs(value) > 10000 or (abs(value) < 0.001 and value != 0):
                return f"{value:.3e}"
            else:
                return f"{value:.3f}"
        else:
            return str(value)

    def format_percentage_value(self, value):
        """Форматирование процентных значений (умножение на 100)"""
        if isinstance(value, (int, float)):
            value_percent = value * 100
            if abs(value_percent) > 10000 or (abs(value_percent) < 0.001 and value_percent != 0):
                return f"{value_percent:.3e}"
            else:
                return f"{value_percent:.3f}"
        else:
            return str(value)

    def draw_zip_scheme(self):
        """Отрисовка схемы ЗИП (оригинальный размер)"""
        try:
            self.update_parameters_from_input(skip_validation=True)

            # Проверяем, есть ли основные геометрические параметры
            if not all([self.D1, self.D2, self.d1, self.d2, self.h1, self.h2, self.h3, self.l0]):
                self.draw_empty_scheme()
                return

        except Exception:
            self.draw_empty_scheme()
            return

        appearance = ctk.get_appearance_mode()
        if appearance.lower().startswith("dark"):
            bg = "#2b2b2b"
            line_color = "white"
        else:
            bg = "white"
            line_color = "black"

        self.ax.clear()
        self.figure.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.ax.set_aspect("equal")

        # Чтение параметров
        D1, D2, d1, d2 = self.D1, self.D2, self.d1, self.d2
        h1, h2, h3, l0 = self.h1, self.h2, self.h3, self.l0

        # Координаты (оригинальные значения)
        y_anchor_bottom = 0
        y_anchor_top = h3
        y_gap_top = y_anchor_top + l0
        y_core_bottom = y_gap_top
        y_core_top = y_core_bottom + h2

        x_left_hole = -d1 / 2
        x_right_hole = d1 / 2
        x_left_core = -D1 / 2
        x_right_core = D1 / 2

        # --- ЯКОРЬ ---
        self.ax.add_patch(Rectangle((x_left_core, 0), D1, h3,
                                    linewidth=2, edgecolor=line_color, facecolor="none"))

        # --- ЗАЗОР l0 ---
        self.ax.plot([0, 0], [y_anchor_top, y_anchor_top + l0],
                     linestyle=":", color=line_color)
        self.ax.text(x_right_core * 0.6, y_anchor_top + l0 / 2,
                     f"l₀ = {self.format_value(l0)} мм", color=line_color, fontsize=9, va="center")

        # --- ОТВЕРСТИЕ d1 ---
        self.ax.plot([x_left_hole, x_left_hole], [y_core_bottom, y_core_top], linewidth=2, color=line_color)
        self.ax.plot([x_right_hole, x_right_hole], [y_core_bottom, y_core_top], linewidth=2, color=line_color)
        self.ax.plot([x_left_hole, x_right_hole], [y_core_bottom, y_core_bottom], linewidth=2, color=line_color)
        self.ax.plot([x_left_hole, x_right_hole], [y_core_top, y_core_top], linewidth=2, color=line_color)

        # --- СЕРДЕЧНИК ---
        self.ax.add_patch(Rectangle((x_left_core, y_core_bottom),
                                    x_left_hole - x_left_core, h2,
                                    linewidth=2, edgecolor=line_color, facecolor="none"))
        self.ax.add_patch(Rectangle((x_right_hole, y_core_bottom),
                                    x_right_core - x_right_hole, h2,
                                    linewidth=2, edgecolor=line_color, facecolor="none"))

        # --- КАТУШКИ ---
        x_left_outer = -D2 / 2
        x_left_inner = -d2 / 2
        x_right_inner = d2 / 2
        x_right_outer = D2 / 2
        y_coil_bottom = y_gap_top
        y_coil_top = y_coil_bottom + h1

        # левая
        self.ax.add_patch(Rectangle((x_left_outer, y_coil_bottom),
                                    x_left_inner - x_left_outer, h1,
                                    linewidth=2, edgecolor=line_color, facecolor="none"))

        # правая
        self.ax.add_patch(Rectangle((x_right_inner, y_coil_bottom),
                                    x_right_outer - x_right_inner, h1,
                                    linewidth=2, edgecolor=line_color, facecolor="none"))

        # --- КРЕСТЫ ---
        def cross(x0, x1, y0, y1):
            self.ax.plot([x0, x1], [y0, y1], color=line_color, linewidth=1)
            self.ax.plot([x0, x1], [y1, y0], color=line_color, linewidth=1)

        cross(x_left_outer, x_left_inner, y_coil_bottom, y_coil_top)
        cross(x_right_inner, x_right_outer, y_coil_bottom, y_coil_top)

        # --- ОСЬ X ---
        y_min = -h3 * 0.4
        y_max = y_core_top + h2 * 0.3
        self.ax.plot([0, 0], [y_min, y_max], linestyle="--", color=line_color)

        # --- ПОДПИСИ ---
        self.ax.text(0, -h3 * 0.5, "3", fontsize=12, fontweight="bold", color=line_color, ha="center")
        self.ax.text(0, y_core_top + h3 * 0.3, "1", fontsize=12, fontweight="bold", color=line_color, ha="center")
        self.ax.text(x_left_outer * 1.05, y_coil_top + h1 * 0.1,
                     "2", fontsize=12, fontweight="bold", color=line_color)

        # --- МАСШТАБ ---
        x_extent = max(D1, D2) / 2 * 1.3
        self.ax.set_xlim(-x_extent, x_extent)
        self.ax.set_ylim(y_min, y_max)
        self.ax.axis("off")

        if hasattr(self, "canvas"):
            self.canvas.draw()

    def update_parameters_from_input(self, skip_validation=False):
        """Обновление параметров из полей ввода"""
        # Сброс подсветок
        for frame in self.input_frames.values():
            frame.configure(fg_color="transparent")

        # Чтение полей
        for key, entry in self.input_entries.items():
            raw = entry.get()
            frame = self.input_frames[key]

            if raw == "":
                if not skip_validation:
                    frame.configure(fg_color="red")
                    raise ValueError(f"Пустое поле: {key}")
                # Для skip_validation устанавливаем 0 для пустых полей
                setattr(self, key, 0.0)
                continue

            try:
                val = float(raw)
                if val < 0 and not skip_validation:
                    frame.configure(fg_color="red")
                    raise ValueError(f"Отрицательное значение: {key}")
                setattr(self, key, val)
            except ValueError:
                if not skip_validation:
                    frame.configure(fg_color="red")
                    raise ValueError(f"Неверный формат числа: {key}")
                # Для skip_validation устанавливаем 0 для неверных форматов
                setattr(self, key, 0.0)

        # Проверка геометрии (только если не skip_validation)
        if not skip_validation:
            self._validate_geometry()

    def _validate_geometry(self):
        """Проверка геометрических условий"""
        errors = []

        # Проверка обязательных полей
        required_fields = ["D1", "D2", "d1", "d2", "h1", "h2", "h3", "l0",
                           "d_n", "p_n_user", "mu_c_user", "z0_user"]

        for param in required_fields:
            if getattr(self, param) == 0:
                errors.append(f"{param} должен быть задан")
                if param in self.input_frames:
                    self.input_frames[param].configure(fg_color="red")

        # Проверка положительных значений для обязательных полей
        for param in required_fields:
            if getattr(self, param) <= 0 and getattr(self, param) != 0:
                errors.append(f"{param} должен быть положительным")
                if param in self.input_frames:
                    self.input_frames[param].configure(fg_color="red")

        # Проверка соотношений (только если все основные параметры заданы)
        if all([self.D1 > 0, self.D2 > 0, self.d1 > 0, self.d2 > 0, self.h1 > 0, self.h2 > 0]):
            if self.D1 <= self.D2:
                errors.append("D1 должен быть больше D2")
                self.input_frames["D1"].configure(fg_color="red")
                self.input_frames["D2"].configure(fg_color="red")

            if self.D2 <= self.d2:
                errors.append("D2 должен быть больше d2")
                self.input_frames["D2"].configure(fg_color="red")
                self.input_frames["d2"].configure(fg_color="red")

            if self.d2 <= self.d1:
                errors.append("d2 должен быть больше d1")
                self.input_frames["d2"].configure(fg_color="red")
                self.input_frames["d1"].configure(fg_color="red")

            if self.h2 <= self.h1:
                errors.append("h2 должен быть больше h1")
                self.input_frames["h2"].configure(fg_color="red")
                self.input_frames["h1"].configure(fg_color="red")

        if self.l0 <= 0:
            errors.append("l0 должен быть положительным")
            self.input_frames["l0"].configure(fg_color="red")

        # Проверка требования по зазору
        if self.l0 <= self.xv:
            errors.append(f"Начальный зазор l0 ({self.l0} мм) должен быть больше диапазона измерения xv ({self.xv} мм)")
            self.input_frames["l0"].configure(fg_color="red")

        if errors:
            error_msg = "Ошибка параметров:\n" + "\n".join(errors)
            messagebox.showerror("Ошибка", error_msg)
            raise ValueError(error_msg)

    def recalculate(self):
        """Выполнение расчета"""
        try:
            self.update_parameters_from_input(skip_validation=False)
            self.draw_zip_scheme()

            # Создание датчика и расчет
            self.sensor = ZIPSensor(
                D1=self.D1, D2=self.D2, d1=self.d1, d2=self.d2,
                h1=self.h1, h2=self.h2, h3=self.h3, l0=self.l0,
                z0=self.z0_user, d_n=self.d_n, xv=self.xv,
                d_zT_min=self.d_zT_min, eta_max=self.eta_max,
                x=self.x, K_kp=self.K_kp, p_n=self.p_n_user,
                mu_0=self.mu_0, mu_c=self.mu_c_user
            )

            self.calculation_results = self.sensor.calc()
            self.update_results_display()

            if self.current_file_path:
                self.file_status_label.configure(text="Файл изменён", text_color="orange")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчёта: {e}")

    def update_results_display(self):
        """Обновление отображения результатов в стиле полей ввода"""
        for w in self.results_container.winfo_children():
            w.destroy()

        if not self.calculation_results:
            return

        # Словарь русских названий
        russian_names = {
            "S_B": "Площадь сечения воздушной части магнитопровода S_B",
            "L_cd": "Длина сечения сердечника L_cd",
            "S_cd": "Площадь сечения сердечника S_cd",
            "S_y": "Площадь сечения якоря S_y",
            "L_y": "Длина якоря L_y",
            "L_c": "Длина магнитопровода L_c",
            "S_c": "Площадь магнитопровода S_c",
            "S_ok": "Площадь окна катушки S_ok",
            "R_cp": "Средний радиус катушки R_cp",
            "N": "Коэффициент размагничивания магнитопровода N",
            "R_mC": "Магнитное сопротивление стальной части R_mC",
            "R_mb": "Зависимость сопротивления от перемещения якоря R_mb",
            "k_B": "Коэффициент k_B",
            "R_B0": "Начальное сопротивление R_B0",
            "k_x": "Коэффициент чувствительности k_x",
            "z_0": "Начальное электрическое сопротивление катушки z_0",
            "Z_x": "Полное электрическое сопротивление катушки Z_x",
            "gamma": "Максимальная приведенная погрешность gamma",
            "q": "Параметр q",
            "gamma_pi": "Гамма пи gamma_pi",
            "d_z": "Максимальная приведенная погрешность d_z",
            "w_0": "Удельное число витков катушки w_0",
            "w": "Число витков катушки w",
            "R_k": "Активное сопротивление катушки R_k",
            "eta": "Доля активного сопротивления катушки eta",
            "f_p": "Частота напряжения питания f_p",
        }

        # Единицы измерения
        units_mapping = {
            'S_B': 'мм²', 'S_cd': 'мм²', 'S_y': 'мм²', 'S_c': 'мм²', 'S_ok': 'мм²',
            'L_cd': 'мм', 'L_y': 'мм', 'L_c': 'мм', 'R_cp': 'мм',
            'z_0': 'Ом', 'Z_x': 'Ом', 'R_k': 'Ом', 'R_B0': 'Ом',
            'f_p': 'Гц',
            'gamma': '%', 'd_z': '%', 'eta': '%',
            'k_x': '1/мм', 'k_B': '1/мм'
        }

        # Группируем результаты по категориям
        categories = {
            "Геометрические параметры": [
                'S_B', 'L_cd', 'S_cd', 'S_y', 'L_y', 'L_c', 'S_c', 'S_ok', 'R_cp'
            ],
            "Магнитные параметры": [
                'N', 'R_mC', 'R_mb', 'k_B', 'R_B0', 'k_x'
            ],
            "Электрические параметры": [
                'z_0', 'Z_x', 'w_0', 'w', 'R_k', 'f_p'
            ],
            "Параметры точности": [
                'gamma', 'q', 'gamma_pi', 'd_z', 'eta'
            ]
        }

        # Вывод результатов по категориям
        for category_name, param_keys in categories.items():
            # Заголовок категории
            category_label = ctk.CTkLabel(
                self.results_container,
                text=category_name,
                font=("Arial", 13, "bold")
            )
            category_label.pack(anchor="w", padx=10, pady=(15, 5))

            # Параметры категории
            for key in param_keys:
                if key in self.calculation_results:
                    value = self.calculation_results[key]

                    # Для процентных параметров умножаем на 100
                    if key in ['gamma', 'd_z', 'eta']:
                        display_value = self.format_percentage_value(value)
                    else:
                        display_value = self.format_value(value)

                    self.create_result_row(
                        russian_names.get(key, key),
                        display_value,
                        units_mapping.get(key, '')
                    )

        # Разделитель
        separator = ctk.CTkFrame(self.results_container, height=2, fg_color="gray")
        separator.pack(fill="x", padx=10, pady=10)

    def create_result_row(self, label_text, value_text, units_text):
        """Создание строки результата в стиле поля ввода"""
        row = ctk.CTkFrame(self.results_container)
        row.pack(fill="x", padx=10, pady=2)

        # Метка параметра
        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            width=300,
            anchor="w"
        )
        lbl.pack(side="left", padx=5)

        # Фрейм для значения и единиц измерения
        value_frame = ctk.CTkFrame(row, fg_color="transparent")
        value_frame.pack(side="right", fill="x", expand=True)

        # Поле с значением (стилизованное под поле ввода)
        value_display = ctk.CTkFrame(value_frame, height=28, border_width=1,
                                     border_color="#cccccc", corner_radius=4)
        value_display.pack(side="left", fill="x", expand=True, padx=(0, 5))
        value_display.pack_propagate(False)

        value_label = ctk.CTkLabel(
            value_display,
            text=value_text,
            font=("Arial", 11),
            anchor="w"
        )
        value_label.pack(fill="both", expand=True, padx=8, pady=4)

        # Единицы измерения
        if units_text:
            units_label = ctk.CTkLabel(
                value_frame,
                text=units_text,
                width=40,
                font=("Arial", 10),
                text_color="gray"
            )
            units_label.pack(side="right", padx=5)

    def clear_parameters(self):
        """Очистка параметров"""
        for k, ent in self.input_entries.items():
            ent.delete(0, "end")
            self.input_frames[k].configure(fg_color="transparent")

        for w in self.results_container.winfo_children():
            w.destroy()

        self.file_status_label.configure(text="Файл не сохранён", text_color="gray")

        self.initial_message = ctk.CTkLabel(
            self.results_container,
            text="Введите параметры и нажмите 'Рассчитать'",
            text_color="gray"
        )
        self.initial_message.pack(pady=20)

        self.calculation_results = None
        self.current_file_path = None
        self.draw_empty_scheme()

    def save_calculation(self):
        """Сохранение расчета в файл"""
        try:
            save_data = {
                "metadata": {
                    "sensor_type": self.selected_sensor,
                    "scheme_type": self.selected_scheme,
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "user_parameters": {
                    k: float(v.get()) if v.get() != "" else None
                    for k, v in self.input_entries.items()
                },
                "calculation_results": self.calculation_results
            }

            if not self.current_file_path:
                path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")]
                )
                if not path:
                    return
                self.current_file_path = path
            else:
                path = self.current_file_path

            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)

            self.file_status_label.configure(
                text=f"Сохранено: {os.path.basename(path)}",
                text_color="green"
            )
            messagebox.showinfo("Успех", f"Файл сохранён:\n{path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_calculation(self):
        """Загрузка расчета из файла"""
        try:
            path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not path:
                return

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "user_parameters" not in data:
                messagebox.showerror("Ошибка", "Неверный формат файла расчёта")
                return

            # Загрузка параметров
            for k, v in data["user_parameters"].items():
                if k in self.input_entries:
                    self.input_entries[k].delete(0, "end")
                    if v is not None:
                        self.input_entries[k].insert(0, str(v))

            # Загрузка результатов
            if data.get("calculation_results"):
                self.calculation_results = data["calculation_results"]
                self.update_results_display()

            self.current_file_path = path
            self.file_status_label.configure(
                text=f"Загружено: {os.path.basename(path)}",
                text_color="blue"
            )
            messagebox.showinfo("Успех", f"Файл загружен:\n{path}")

            self.update_parameters_from_input(skip_validation=True)
            self.draw_zip_scheme()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def print_results(self):
        """Печать результатов"""
        if not self.calculation_results:
            messagebox.showwarning("Предупреждение", "Нет данных для печати. Сначала выполните расчет.")
            return

        try:
            import tempfile
            import webbrowser

            html_content = self._generate_printable_html()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            webbrowser.open(f'file://{temp_file}')

            messagebox.showinfo("Печать",
                                "Файл для печати открыт в браузере. Используйте Ctrl+P для печати.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать файл для печати: {str(e)}")

    def save_as_html(self):
        """Сохранение в HTML"""
        if not self.calculation_results:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения. Сначала выполните расчет.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                title="Сохранить результаты как HTML"
            )

            if not filename:
                return

            html_content = self._generate_printable_html()

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            messagebox.showinfo("Сохранено", f"Результаты сохранены в файл:\n{filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _generate_printable_html(self):
        """Генерация HTML для печати"""
        russian_names = {
            "xv": "Диапазон измерений xv, мм",
            "d_zT_min": "Минимальная погрешность d_zT_min, %",
            "eta_max": "Максимальный КПД eta_max",
            "x": "Относительная погрешность x",
            "K_kp": "Коэффициент использования K_kp",
            "mu_0": "Магнитная проницаемость вакуума mu_0",
            "D1": "Внешний диаметр D1, мм",
            "D2": "Внешний диаметр D2, мм",
            "d1": "Диаметр отверстия d1, мм",
            "d2": "Диаметр отверстия d2, мм",
            "h1": "Высота катушки h1, мм",
            "h2": "Высота сердечника h2, мм",
            "h3": "Толщина якоря h3, мм",
            "l0": "Начальный зазор l0, мм",
            "d_n": "Диаметр провода d_n, мм",
            "p_n_user": "Удельное сопротивление меди p_n, Ом·мм²/м",
            "mu_c_user": "Магнитная проницаемость mu_c",
            "z0_user": "Начальное сопротивление z0, Ом",
            "S_B": "Площадь сечения воздушной части магнитопровода S_B, мм²",
            "L_cd": "Длина сечения сердечника L_cd, мм",
            "S_cd": "Площадь сечения сердечника S_cd, мм²",
            "S_y": "Площадь сечения якоря S_y, мм²",
            "L_y": "Длина якоря L_y, мм",
            "L_c": "Длина магнитопровода L_c, мм",
            "S_c": "Площадь магнитопровода S_c, мм²",
            "S_ok": "Площадь окна катушки S_ok, мм²",
            "R_cp": "Средний радиус катушки R_cp, мм",
            "N": "Коэффициент размагничивания магнитопровода N",
            "R_mC": "Магнитное сопротивление стальной части R_mC",
            "R_mb": "Зависимость сопротивления от перемещения якоря R_mb",
            "k_B": "Коэффициент k_B",
            "w_0": "Удельное число витков катушки w_0",
            "w": "Число витков катушки w",
            "R_k": "Активное сопротивление катушки R_k, Ом",
            "f_p": "Частота напряжения питания f_p, Гц",
            "eta": "Доля активного сопротивления катушки eta",
            "gamma": "Максимальная приведенная погрешность gamma, %",
            "q": "Параметр q",
            "d_z": "Максимальная приведенная погрешность d_z, %",
            "Z_x": "Полное электрическое сопротивление катушки Z_x, Ом",
        }

        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Результаты расчета ДЗИП</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 20px;
                    line-height: 1.4;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #2E8B57;
                    padding-bottom: 15px;
                    margin-bottom: 25px;
                }}
                .section {{
                    margin-bottom: 25px;
                    page-break-inside: avoid;
                }}
                .section-title {{
                    background-color: #f8f9fa;
                    padding: 8px 12px;
                    border-left: 4px solid #2E8B57;
                    margin-bottom: 12px;
                    font-weight: bold;
                }}
                .param-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-size: 12px;
                }}
                .param-table th {{
                    background-color: #2E8B57;
                    color: white;
                    padding: 8px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                .param-table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                .param-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .result-value {{
                    font-weight: bold;
                    color: #2E8B57;
                }}
                .metadata {{
                    font-size: 11px;
                    color: #666;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                }}
                @media print {{
                    body {{ margin: 15mm; }}
                    .no-print {{ display: none; }}
                    .section {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>РЕЗУЛЬТАТЫ РАСЧЕТА ПАРАМЕТРОВ ДАТЧИКА ДЗИП</h1>
                <p>Тип датчика: {self.selected_sensor} | Схема подключения: {self.selected_scheme}</p>
                <p>Дата расчета: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</p>
            </div>

            {self._generate_input_params_section(russian_names)}
            {self._generate_results_section(russian_names)}
            {self._generate_notes_section()}

            <div class="metadata">
                <p>Сгенерировано автоматически в программе расчета ДЗИП</p>
            </div>

            <div class="no-print" style="text-align: center; margin-top: 30px;">
                <p><em>Для печати используйте Ctrl+P</em></p>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_input_params_section(self, russian_names):
        """Генерация секции входных параметров"""
        input_params_html = """
        <div class="section">
            <div class="section-title">ВХОДНЫЕ ПАРАМЕТРЫ</div>
            <table class="param-table">
                <tr>
                    <th>Параметр</th>
                    <th>Значение</th>
                    <th>Единицы измерения</th>
                </tr>
        """

        # Основные параметры
        main_params = {
            "Тип датчика": self.selected_sensor,
            "Схема подключения": self.selected_scheme
        }

        for param, value in main_params.items():
            input_params_html += f"""
                <tr>
                    <td>{param}</td>
                    <td class="result-value">{value}</td>
                    <td>-</td>
                </tr>
            """

        # Основные и общие параметры
        basic_common_params = ["xv", "d_zT_min", "eta_max", "x", "K_kp", "mu_0"]
        for param in basic_common_params:
            value = getattr(self, param, "N/A")
            units = self._get_units_from_param_name(param)

            # Для процентных параметров умножаем на 100
            if param == 'd_zT_min':
                display_value = self.format_percentage_value(value)
            else:
                display_value = self.format_value(value)

            input_params_html += f"""
                <tr>
                    <td>{russian_names.get(param, param)}</td>
                    <td class="result-value">{display_value}</td>
                    <td>{units}</td>
                </tr>
            """

        # Геометрические параметры
        geom_params = ["D1", "D2", "d1", "d2", "h1", "h2", "h3", "l0"]
        for param in geom_params:
            value = getattr(self, param, "N/A")
            input_params_html += f"""
                <tr>
                    <td>{russian_names.get(param, param)}</td>
                    <td class="result-value">{self.format_value(value)}</td>
                    <td>мм</td>
                </tr>
            """

        # Электрические параметры
        elec_params = ["d_n", "p_n_user", "mu_c_user", "z0_user"]
        for param in elec_params:
            value = getattr(self, param, "N/A")
            units = "Ом·мм²/м" if param == "p_n_user" else "Ом" if param == "z0_user" else "мм" if param == "d_n" else "-"
            input_params_html += f"""
                <tr>
                    <td>{russian_names.get(param, param)}</td>
                    <td class="result-value">{self.format_value(value)}</td>
                    <td>{units}</td>
                </tr>
            """

        input_params_html += """
            </table>
        </div>
        """
        return input_params_html

    def _generate_results_section(self, russian_names):
        """Генерация секции результатов"""
        if not self.calculation_results:
            return "<div class='section'><p>Результаты расчета отсутствуют</p></div>"

        results_html = """
        <div class="section">
            <div class="section-title">РЕЗУЛЬТАТЫ РАСЧЕТА</div>
            <table class="param-table">
                <tr>
                    <th>Параметр</th>
                    <th>Значение</th>
                    <th>Единицы измерения</th>
                </tr>
        """

        for key, value in self.calculation_results.items():
            # Для процентных параметров умножаем на 100
            if key in ['gamma', 'd_z', 'eta']:
                formatted_value = self.format_percentage_value(value)
            else:
                formatted_value = self.format_value(value)

            units = self._get_units_from_param_name(key)

            results_html += f"""
                <tr>
                    <td>{russian_names.get(key, key)}</td>
                    <td class="result-value">{formatted_value}</td>
                    <td>{units}</td>
                </tr>
            """

        results_html += """
            </table>
        </div>
        """
        return results_html

    def _generate_notes_section(self):
        """Генерация секции примечаний"""
        return """
        <div class="section">
            <div class="section-title">ПРИМЕЧАНИЯ</div>
            <ul>
                <li>Все геометрические параметры указаны в миллиметрах (мм)</li>
                <li>Электрические параметры рассчитаны для заданных условий</li>
                <li>Погрешности указаны в процентах (%)</li>
                <li>Расчет выполнен по методике для дифференциального законченного ИП</li>
                <li>Все значения округлены до 3 знаков после запятой</li>
            </ul>
        </div>
        """

    def _get_units_from_param_name(self, param_name):
        """Определение единиц измерения по названию параметра"""
        units_mapping = {
            'xv': 'мм', 'd_zT_min': '%', 'eta_max': '', 'x': '', 'K_kp': '',
            'mu_0': 'Гн/м',
            'S_B': 'мм²', 'S_cd': 'мм²', 'S_y': 'мм²', 'S_c': 'мм²', 'S_ok': 'мм²',
            'L_cd': 'мм', 'L_y': 'мм', 'L_c': 'мм', 'R_cp': 'мм',
            'z_0': 'Ом', 'Z_x': 'Ом', 'R_k': 'Ом', 'R_B0': 'Ом',
            'f_p': 'Гц',
            'gamma': '%', 'd_z': '%', 'eta': '%',
            'k_x': '1/мм', 'k_B': '1/мм'
        }
        return units_mapping.get(param_name, '-')