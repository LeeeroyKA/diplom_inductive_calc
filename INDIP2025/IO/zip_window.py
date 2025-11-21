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
    def __init__(self, parent, params):
        super().__init__(parent)
        self.title("ДЗИП — Расчёт и схема")
        self.geometry("1400x800")
        self.params = params or {}
        self.sensor = None
        self.calculation_results = None
        self.current_file_path = None

        # инициализация параметров
        self.init_parameters()

        # разметка окна
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # создаём виджеты
        self.create_widgets()

    # --------------------- ИНИЦИАЛИЗАЦИЯ ---------------------
    def init_parameters(self):
        self.xv = self.params.get("xv", 0.0)
        self.d_zT_min = self.params.get("d_zT_min", 0.0)
        self.selected_sensor = self.params.get("selected_sensor", "ДЗИП")
        self.selected_scheme = self.params.get("selected_scheme", "ПРСМ")

        self.eta_max = 5
        self.x = 0.003
        self.K_kp = 1
        self.p_n = 17.5e-6
        self.mu_c = 3000
        self.mu_0 = 4 * 3.141592653589793e-7
        self.z0 = 1000
        self.z_0_eta = 2000

        # Геометрия по умолчанию
        self.D1 = 50.0
        self.D2 = 40.0
        self.d1 = 10.0
        self.d2 = 20.0
        self.h1 = 30.0
        self.h2 = 25.0
        self.h3 = 5.0
        self.l0 = 2.0

        # Электрика
        self.d_n = 0.5
        self.p_n_user = 0.0000175
        self.mu_c_user = 3000
        self.z0_user = 1000

    # --------------------- UI ---------------------
    def create_widgets(self):
        self.left_frame = ctk.CTkScrollableFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        header = ctk.CTkLabel(self.left_frame, text="ПАРАМЕТРЫ РАСЧЁТА", font=("Arial", 16, "bold"))
        header.pack(pady=8)

        self.input_entries = {}
        self.input_frames = {}  # для подсветок
        self._create_input_rows()

        # кнопки
        self._create_buttons()

        # статус файла
        self.file_status_label = ctk.CTkLabel(self.left_frame, text="Файл не сохранён", text_color="gray")
        self.file_status_label.pack(pady=6)

        # правая часть
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # схема
        self.scheme_frame = ctk.CTkFrame(self.right_frame)
        self.scheme_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        label = ctk.CTkLabel(self.scheme_frame, text="Расчётная схема ЗИП", font=("Arial", 14, "bold"))
        label.pack(pady=4)

        self._create_scheme_canvas()

        # результаты
        self.results_frame = ctk.CTkFrame(self.right_frame)
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        rlabel = ctk.CTkLabel(self.results_frame, text="РЕЗУЛЬТАТЫ РАСЧЁТА", font=("Arial", 14, "bold"))
        rlabel.pack(pady=6)
        self.results_scroll = ctk.CTkScrollableFrame(self.results_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=6, pady=6)
        self.results_container = ctk.CTkFrame(self.results_scroll)
        self.results_container.pack(fill="both", expand=True)

        self.initial_message = ctk.CTkLabel(self.results_container,
                                            text="Введите параметры и нажмите 'Рассчитать'",
                                            text_color="gray")
        self.initial_message.pack(pady=20)

    # --------------------- Ввод параметров ---------------------
    def _create_input_rows(self):
        geom_label = ctk.CTkLabel(self.left_frame, text="Геометрические параметры:", font=("Arial", 12, "bold"))
        geom_label.pack(pady=(6, 4), anchor="w")

        geom_params = [
            ("Внешний диаметр D1, мм:", "D1", str(self.D1)),
            ("Внешний диаметр D2, мм:", "D2", str(self.D2)),
            ("Диаметр отв. d1, мм:", "d1", str(self.d1)),
            ("Диаметр отв. d2, мм:", "d2", str(self.d2)),
            ("Высота катушки h1, мм:", "h1", str(self.h1)),
            ("Высота сердечника h2, мм:", "h2", str(self.h2)),
            ("Толщина якоря h3, мм:", "h3", str(self.h3)),
            ("Начальный зазор l0, мм:", "l0", str(self.l0)),
        ]

        for label_text, name, default in geom_params:
            row = ctk.CTkFrame(self.left_frame)
            row.pack(fill="x", padx=6, pady=2)

            lbl = ctk.CTkLabel(row, text=label_text, width=180)
            lbl.pack(side="left", padx=4)

            # рамка для подсветки
            frame = ctk.CTkFrame(row, fg_color="transparent")
            frame.pack(side="right", fill="x", expand=True)

            ent = ctk.CTkEntry(frame)
            ent.insert(0, default)
            ent.pack(fill="x", padx=4)

            self.input_entries[name] = ent
            self.input_frames[name] = frame

        elec_label = ctk.CTkLabel(self.left_frame, text="Электрические параметры:", font=("Arial", 12, "bold"))
        elec_label.pack(pady=(10, 4), anchor="w")

        elec_params = [
            ("Диаметр провода d_n, мм:", "d_n", str(self.d_n)),
            ("Уд. сопр. меди p_n, Ом·мм²/м:", "p_n", str(self.p_n_user)),
            ("Магн. прониц. mu_c:", "mu_c", str(self.mu_c_user)),
            ("Нач. сопр. z0, Ом:", "z0", str(self.z_0_eta)),
        ]

        for label_text, name, default in elec_params:
            row = ctk.CTkFrame(self.left_frame)
            row.pack(fill="x", padx=6, pady=2)

            lbl = ctk.CTkLabel(row, text=label_text, width=180)
            lbl.pack(side="left", padx=4)

            frame = ctk.CTkFrame(row, fg_color="transparent")
            frame.pack(side="right", fill="x", expand=True)

            ent = ctk.CTkEntry(frame)
            ent.insert(0, default)
            ent.pack(fill="x", padx=4)

            self.input_entries[name] = ent
            self.input_frames[name] = frame

    # --------------------- Кнопки ---------------------
    def _create_buttons(self):
        btn_frame = ctk.CTkFrame(self.left_frame)
        btn_frame.pack(fill="x", padx=6, pady=8)

        ctk.CTkButton(btn_frame, text="Обновить схему",
                      fg_color="#FF8C00", command=self.draw_zip_scheme) \
            .pack(side="left", padx=4, expand=True)

        ctk.CTkButton(btn_frame, text="Рассчитать",
                      command=self.recalculate) \
            .pack(side="left", padx=4, expand=True)

        ctk.CTkButton(btn_frame, text="Очистить",
                      command=self.clear_parameters) \
            .pack(side="right", padx=4, expand=True)

        # Панель сохранения/загрузки
        file_frame = ctk.CTkFrame(self.left_frame)
        file_frame.pack(fill="x", padx=6, pady=(10, 0))

        ctk.CTkButton(file_frame, text="Сохранить расчет",
                      fg_color="#2E8B57", hover_color="#3CB371",
                      command=self.save_calculation) \
            .pack(side="left", padx=4, expand=True)

        ctk.CTkButton(file_frame, text="Загрузить расчет",
                      fg_color="#4169E1", hover_color="#6495ED",
                      command=self.load_calculation) \
            .pack(side="right", padx=4, expand=True)

    # --------------------- CANVAS ---------------------
    def _create_scheme_canvas(self):
        appearance = ctk.get_appearance_mode()
        facecolor = "white" if appearance.lower().startswith("light") else "#2b2b2b"
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=80)
        self.figure.patch.set_facecolor(facecolor)
        self.ax.set_facecolor(facecolor)
        self.ax.set_aspect("equal")

        self.draw_zip_scheme()

        self.canvas = FigureCanvasTkAgg(self.figure, self.scheme_frame)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=6, pady=6)

    # --------------------- ОТРИСОВКА СХЕМЫ ---------------------
    def draw_zip_scheme(self):
        try:
            self.update_parameters_from_input(skip_validation=True)
        except Exception:
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

        # чтение параметров
        D1, D2, d1, d2 = self.D1, self.D2, self.d1, self.d2
        h1, h2, h3, l0 = self.h1, self.h2, self.h3, self.l0

        # Координаты
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
                     f"l₀ = {l0:.1f} мм", color=line_color, fontsize=9, va="center")

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

    # --------------------- ПАРАМЕТРЫ ---------------------
    def update_parameters_from_input(self, skip_validation=False):
        # Сброс всех подсветок
        for frame in self.input_frames.values():
            frame.configure(fg_color="transparent")

        # Чтение полей и проверка на неотрицательные значения
        for key, entry in self.input_entries.items():
            raw = entry.get()
            frame = self.input_frames[key]

            if raw == "":
                if not skip_validation:
                    frame.configure(fg_color="red")
                    raise ValueError(f"Пустое поле: {key}")
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

        # Проверка геометрических условий
        if not skip_validation:
            self._validate_geometry()

    def _validate_geometry(self):
        """Проверка геометрических условий с подсветкой проблемных полей"""
        errors = []

        # Проверка на положительные значения
        for param in ["D1", "D2", "d1", "d2", "h1", "h2", "h3", "l0"]:
            if getattr(self, param) <= 0:
                errors.append(f"{param} должен быть положительным")
                self.input_frames[param].configure(fg_color="red")

        # Проверка геометрических соотношений
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

        # Проверка электрических параметров
        if self.d_n <= 0:
            errors.append("d_n должен быть положительным")
            self.input_frames["d_n"].configure(fg_color="red")

        if self.p_n_user <= 0:
            errors.append("p_n должен быть положительным")
            self.input_frames["p_n"].configure(fg_color="red")

        if self.mu_c_user <= 0:
            errors.append("mu_c должен быть положительным")
            self.input_frames["mu_c"].configure(fg_color="red")

        if self.z0_user <= 0:
            errors.append("z0 должен быть положительным")
            self.input_frames["z0"].configure(fg_color="red")

        if errors:
            error_msg = "Ошибка параметров:\n" + "\n".join(errors)
            messagebox.showerror("Ошибка", error_msg)
            raise ValueError(error_msg)

    # --------------------- ЛОГИКА ---------------------
    def update_scheme(self):
        try:
            self.update_parameters_from_input(skip_validation=True)
        except:
            return
        self.draw_zip_scheme()

    def recalculate(self):
        try:
            self.update_parameters_from_input(skip_validation=False)
            self.update_scheme()

            # Проверка дополнительных условий перед расчетом
            if self.l0 <= self.xv:
                messagebox.showerror("Ошибка", "Начальный зазор l0 должен быть больше диапазона измерения xv")
                self.input_frames["l0"].configure(fg_color="red")
                return

            self.sensor = ZIPSensor(
                D1=self.D1, D2=self.D2, d1=self.d1, d2=self.d2,
                h1=self.h1, h2=self.h2, h3=self.h3, l0=self.l0,
                z0=self.z0_user, d_n=self.d_n, xv=self.xv,
                d_zT_min=self.d_zT_min, eta_max=self.eta_max,
                x=self.x, K_kp=self.K_kp, p_n=self.p_n_user,
                mu_0=self.mu_0, mu_c=self.mu_c_user, z_0_eta=self.z_0_eta
            )

            self.calculation_results = self.sensor.calc()
            self.update_results_display()

            if self.current_file_path:
                self.file_status_label.configure(text="Файл изменён", text_color="orange")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчёта: {e}")

    def update_results_display(self):
        for w in self.results_container.winfo_children():
            w.destroy()

        if not self.calculation_results:
            return

        # Словарь для перевода названий параметров на русский
        russian_names = {
            # Геометрические параметры
            "D1": "Внешний диаметр D1",
            "D2": "Внешний диаметр D2",
            "d1": "Диаметр отверстия d1",
            "d2": "Диаметр отверстия d2",
            "h1": "Высота катушки h1",
            "h2": "Высота сердечника h2",
            "h3": "Толщина якоря h3",
            "l0": "Начальный зазор l0",

            # Электрические параметры
            "d_n": "Диаметр провода d_n",
            "p_n": "Удельное сопротивление меди p_n",
            "mu_c": "Магнитная проницаемость mu_c",
            "z0": "Начальное сопротивление z0",

            # Результаты расчетов
            "S_B": "Площадь сечения воздушной части магнитопровода S_B",
            "L_cd": "Длина сечения сердечника L_cd",
            "S_cd": "Площадь сечения сердечника S_cd",
            "S_y": "Площадь сечения якоря S_y",
            "L_y": "Длина якоря L_y",
            "L_c": "Длина магнитопровода L_c",
            "S_c": "Площадь магнитопровода S_c",
            "S_ok": "Площадь окна катушки S_ok",
            "R_cp": "Средний радиус катушки R_cp",
            "R_B": "Сопротивление воздушной части магнитопровода R_B",
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

            # Дополнительные параметры
            "xv": "Максимальный диапазон измерения xv",
            "d_zT_min": "Минимальная погрешность d_zT_min",
            "eta_max": "Максимальный КПД eta_max",
            "x": "Перемещение x",
            "K_kp": "Коэффициент заполнения K_kp",
            "mu_0": "Магнитная постоянная mu_0",
            "z_0_eta": "Начальное сопротивление для КПД z_0_eta"
        }

        # Вывод результатов с русскими названиями
        for key, value in self.calculation_results.items():
            # Берем русское название из словаря, или оставляем оригинал если нет перевода
            russian_key = russian_names.get(key, key)

            # Форматируем значение в зависимости от типа
            if isinstance(value, (int, float)):
                # Для чисел используем научную нотацию для очень больших/маленьких чисел
                if abs(value) > 10000 or (abs(value) < 0.001 and value != 0):
                    formatted_value = f"{value:.4e}"
                else:
                    formatted_value = f"{value:.6f}"
            else:
                formatted_value = str(value)

            lbl = ctk.CTkLabel(self.results_container,
                               text=f"{russian_key}: {formatted_value}",
                               font=("Arial", 12))
            lbl.pack(anchor="w", padx=10, pady=3)

        # Добавляем разделитель если есть результаты
        if self.calculation_results:
            separator = ctk.CTkFrame(self.results_container, height=2, fg_color="gray")
            separator.pack(fill="x", padx=10, pady=5)

    def clear_parameters(self):
        for k, ent in self.input_entries.items():
            ent.delete(0, "end")
            self.input_frames[k].configure(fg_color="transparent")

        for w in self.results_container.winfo_children():
            w.destroy()

        self.file_status_label.configure(text="Файл не сохранён", text_color="gray")

        self.initial_message = ctk.CTkLabel(self.results_container,
                                            text="Введите параметры и нажмите 'Рассчитать'",
                                            text_color="gray")
        self.initial_message.pack(pady=20)

        self.calculation_results = None
        self.current_file_path = None

    # --------------------- JSON SAVE / LOAD ---------------------
    def save_calculation(self):
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
                path = filedialog.asksaveasfilename(defaultextension=".json",
                                                    filetypes=[("JSON files", "*.json")])
                if not path:
                    return

                self.current_file_path = path
            else:
                path = self.current_file_path

            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)

            self.file_status_label.configure(text=f"Сохранено: {os.path.basename(path)}", text_color="green")
            messagebox.showinfo("Успех", f"Файл сохранён:\n{path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_calculation(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not path:
                return

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "user_parameters" not in data:
                messagebox.showerror("Ошибка", "Неверный формат файла расчёта")
                return

            for k, v in data["user_parameters"].items():
                if k in self.input_entries:
                    self.input_entries[k].delete(0, "end")
                    if v is not None:
                        self.input_entries[k].insert(0, str(v))

            if data.get("calculation_results"):
                self.calculation_results = data["calculation_results"]
                self.update_results_display()

            self.current_file_path = path
            self.file_status_label.configure(text=f"Загружено: {os.path.basename(path)}", text_color="blue")
            messagebox.showinfo("Успех", f"Файл загружен:\n{path}")

            self.update_parameters_from_input(skip_validation=True)
            self.draw_zip_scheme()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")