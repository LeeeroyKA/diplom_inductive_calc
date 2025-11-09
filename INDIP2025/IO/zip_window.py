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

    def init_parameters(self):
        # параметры из GUI (главного окна)
        self.xv = self.params.get("xv", 0.0)
        self.d_zT_min = self.params.get("d_zT_min", 0.0)
        self.selected_sensor = self.params.get("selected_sensor", "ДЗИП")
        self.selected_scheme = self.params.get("selected_scheme", "ПРСМ")

        # фиксированные (по умолчанию)
        self.eta_max = 5
        self.x = 0.003
        self.K_kp = 1
        self.p_n = 17.5 * 10 ** -6
        self.mu_c = 3000
        self.mu_0 = 4 * 3.141592653589793 * 10 ** -7
        self.z0 = 1000
        self.z_0_eta = 2000

        # геометрические значения по умолчанию (мм)
        self.D1 = 50.0
        self.D2 = 40.0
        self.d1 = 10.0
        self.d2 = 20.0
        self.h1 = 30.0
        self.h2 = 25.0
        self.h3 = 5.0
        self.l0 = 2.0

        # электрические значения по умолчанию
        self.d_n = 0.5
        self.p_n_user = 0.0000175
        self.mu_c_user = 3000
        self.z0_user = 1000

    # ---------------- UI ----------------
    def create_widgets(self):
        # левая колонка — ввод параметров и кнопки
        self.left_frame = ctk.CTkScrollableFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        header = ctk.CTkLabel(self.left_frame, text="ПАРАМЕТРЫ РАСЧЁТА", font=("Arial", 16, "bold"))
        header.pack(pady=8)

        self.input_entries = {}
        self._create_input_rows()

        # кнопки
        self._create_buttons()

        # статус файла
        self.file_status_label = ctk.CTkLabel(self.left_frame, text="Файл не сохранён", text_color="gray")
        self.file_status_label.pack(pady=6)

        # правая колонка — схема и результаты
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # панель схемы
        self.scheme_frame = ctk.CTkFrame(self.right_frame)
        self.scheme_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        label = ctk.CTkLabel(self.scheme_frame, text="Расчётная схема ЗИП", font=("Arial", 14, "bold"))
        label.pack(pady=4)

        self._create_scheme_canvas()

        # панель результатов
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
            frame = ctk.CTkFrame(self.left_frame)
            frame.pack(fill="x", padx=6, pady=2)
            lbl = ctk.CTkLabel(frame, text=label_text, width=180)
            lbl.pack(side="left", padx=4)
            ent = ctk.CTkEntry(frame)
            ent.insert(0, default)
            ent.pack(side="right", fill="x", expand=True, padx=4)
            self.input_entries[name] = ent

        elec_label = ctk.CTkLabel(self.left_frame, text="Электрические параметры:", font=("Arial", 12, "bold"))
        elec_label.pack(pady=(10, 4), anchor="w")

        elec_params = [
            ("Диаметр провода d_n, мм:", "d_n", str(self.d_n)),
            ("Уд. сопр. меди p_n, Ом*мм²/м:", "p_n", str(self.p_n_user)),
            ("Магн. прониц. mu_c:", "mu_c", str(self.mu_c_user)),
            ("Нач. сопр. z0, Ом:", "z0", str(self.z0_user)),
        ]
        for label_text, name, default in elec_params:
            frame = ctk.CTkFrame(self.left_frame)
            frame.pack(fill="x", padx=6, pady=2)
            lbl = ctk.CTkLabel(frame, text=label_text, width=180)
            lbl.pack(side="left", padx=4)
            ent = ctk.CTkEntry(frame)
            ent.insert(0, default)
            ent.pack(side="right", fill="x", expand=True, padx=4)
            self.input_entries[name] = ent

    def _create_buttons(self):
        btn_frame = ctk.CTkFrame(self.left_frame)
        btn_frame.pack(fill="x", padx=6, pady=8)

        ctk.CTkButton(btn_frame, text="Обновить схему", fg_color="#FF8C00",
                      command=self.draw_zip_scheme).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(btn_frame, text="Рассчитать", command=self.recalculate).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(btn_frame, text="Очистить", command=self.clear_parameters).pack(side="right", padx=4, expand=True)

        file_frame = ctk.CTkFrame(self.left_frame)
        file_frame.pack(fill="x", padx=6, pady=(4, 0))
        ctk.CTkButton(file_frame, text="Сохранить расчет", fg_color="#2E8B57", hover_color="#3CB371",
                      command=self.save_calculation).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(file_frame, text="Загрузить расчет", fg_color="#4169E1", hover_color="#6495ED",
                      command=self.load_calculation).pack(side="right", padx=4, expand=True)

    def _create_scheme_canvas(self):
        # создаём matplotlib-фигуру и Canvas
        appearance = ctk.get_appearance_mode()
        facecolor = "white" if appearance.lower().startswith("light") else "#2b2b2b"
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=80)
        self.figure.patch.set_facecolor(facecolor)
        self.ax.set_facecolor(facecolor)
        self.ax.set_aspect("equal")

        # начальная отрисовка
        self.draw_zip_scheme()

        self.canvas = FigureCanvasTkAgg(self.figure, self.scheme_frame)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=6, pady=6)

    # ---------------- Отрисовка схемы ----------------
    def draw_zip_scheme(self):
        """
        Итерация 8:
        Добавлены катушки (2) с крестовой штриховкой.
        """
        try:
            self.update_parameters_from_input(skip_validation=True)
        except Exception:
            pass

        # Цветовая схема
        appearance = ctk.get_appearance_mode()
        if appearance.lower().startswith('dark'):
            bg = '#2b2b2b'
            line_color = 'white'
        else:
            bg = 'white'
            line_color = 'black'

        self.ax.clear()
        self.figure.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.ax.set_aspect('equal')

        # --- Параметры ---
        def safe_float(attr, default):
            try:
                return float(attr)
            except Exception:
                return default

        D1 = safe_float(self.D1, 50.0)
        D2 = safe_float(self.D2, 40.0)
        d1 = safe_float(self.d1, 10.0)
        d2 = safe_float(self.d2, 20.0)
        h1 = safe_float(self.h1, 5.0)
        h2 = safe_float(self.h2, 8.0)
        h3 = safe_float(self.h3, 5.0)
        l0 = safe_float(self.l0, 2.0)

        # Координаты по высоте
        y_anchor_bottom = 0
        y_anchor_top = y_anchor_bottom + h3
        y_gap_top = y_anchor_top + l0
        y_core_bottom = y_gap_top
        y_core_top = y_core_bottom + h2

        # По ширине
        x_left_hole = -d1 / 2
        x_right_hole = d1 / 2
        x_left_core = -D1 / 2
        x_right_core = D1 / 2

        # --- 1. Якорь (3) ---
        self.ax.add_patch(Rectangle((x_left_core, y_anchor_bottom), D1, h3,
                                    linewidth=2, edgecolor=line_color, facecolor='none'))

        # --- 2. Зазор l0 (пунктир) ---
        self.ax.plot([0, 0], [y_anchor_top, y_anchor_top + l0],
                     linestyle=':', color=line_color, linewidth=1.2)
        self.ax.text(x_right_core * 0.6, y_anchor_top + l0 / 2,
                     f"l₀ = {l0:.1f} мм", color=line_color, fontsize=9, va='center')

        # --- 3. Отверстие (d1) ---
        self.ax.plot([x_left_hole, x_left_hole], [y_core_bottom, y_core_top], color=line_color, linewidth=2)
        self.ax.plot([x_right_hole, x_right_hole], [y_core_bottom, y_core_top], color=line_color, linewidth=2)
        self.ax.plot([x_left_hole, x_right_hole], [y_core_bottom, y_core_bottom], color=line_color, linewidth=2)
        self.ax.plot([x_left_hole, x_right_hole], [y_core_top, y_core_top], color=line_color, linewidth=2)

        # --- 4. Сердечник (1) ---
        core_height = h2
        self.ax.add_patch(Rectangle((x_left_core, y_core_bottom),
                                    x_left_hole - x_left_core, core_height,
                                    linewidth=2, edgecolor=line_color, facecolor='none'))
        self.ax.add_patch(Rectangle((x_right_hole, y_core_bottom),
                                    x_right_core - x_right_hole, core_height,
                                    linewidth=2, edgecolor=line_color, facecolor='none'))

        # --- 5. Катушки (2) ---
        x_left_coil_outer = -D2 / 2
        x_left_coil_inner = -d2 / 2
        x_right_coil_inner = d2 / 2
        x_right_coil_outer = D2 / 2
        y_coil_bottom = y_gap_top
        y_coil_top = y_coil_bottom + h1

        # Левая катушка
        self.ax.add_patch(Rectangle((x_left_coil_outer, y_coil_bottom),
                                    x_left_coil_inner - x_left_coil_outer, h1,
                                    linewidth=2, edgecolor=line_color, facecolor='none'))
        # Правая катушка
        self.ax.add_patch(Rectangle((x_right_coil_inner, y_coil_bottom),
                                    x_right_coil_outer - x_right_coil_inner, h1,
                                    linewidth=2, edgecolor=line_color, facecolor='none'))

        # --- 6. Штриховка крестом внутри катушек ---
        def draw_cross(x0, x1, y0, y1):
            self.ax.plot([x0, x1], [y0, y1], color=line_color, linewidth=1)
            self.ax.plot([x0, x1], [y1, y0], color=line_color, linewidth=1)

        # левая катушка
        draw_cross(x_left_coil_outer, x_left_coil_inner, y_coil_bottom, y_coil_top)
        # правая катушка
        draw_cross(x_right_coil_inner, x_right_coil_outer, y_coil_bottom, y_coil_top)

        # --- 7. Центральная ось ---
        y_min = -h3 * 0.4
        y_max = y_core_top + h2 * 0.3
        self.ax.plot([0, 0], [y_min, y_max], linestyle='--', color=line_color, linewidth=1)
        self.ax.text(0, y_max, "x=0", color=line_color, ha='center', va='bottom', fontsize=9)

        # --- Подписи элементов ---
        self.ax.text(0, -h3 * 0.5, "3", color=line_color, fontsize=12, fontweight='bold', ha='center')
        self.ax.text(0, y_core_top + h3 * 0.3, "1", color=line_color, fontsize=12, fontweight='bold', ha='center')
        self.ax.text(x_left_coil_outer * 1.05, y_coil_top + h1 * 0.1, "2", color=line_color, fontsize=12,
                     fontweight='bold')

        # --- Масштабирование ---
        x_extent = max(D1, D2) / 2 * 1.3
        self.ax.set_xlim(-x_extent, x_extent)
        self.ax.set_ylim(y_min, y_max)
        self.ax.axis('off')

        if getattr(self, "canvas", None):
            self.canvas.draw()

    # ---------------- Логика/Кнопки ----------------
    def update_parameters_from_input(self, skip_validation=False):
        # читаем все поля ввода в self.input_entries и присваиваем атрибутам
        try:
            for key, entry in self.input_entries.items():
                val = entry.get()
                if val == "":
                    # не переписываем пустыми
                    continue
                try:
                    numeric = float(val)
                    setattr(self, key, numeric)
                except ValueError:
                    # если не получилось, бросаем, если требуется валидация
                    if not skip_validation:
                        raise ValueError(f"Неверное значение для {key}: {val}")
        except Exception:
            if not skip_validation:
                raise

    def update_scheme(self):
        try:
            self.update_parameters_from_input(skip_validation=True)
        except Exception:
            pass
        self.draw_zip_scheme()

    def recalculate(self):
        try:
            self.update_parameters_from_input(skip_validation=False)
            self.update_scheme()

            # создаём модель и считаем
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
        # очистка контейнера
        for w in self.results_container.winfo_children():
            w.destroy()

        if not self.calculation_results:
            return

        # вывод результатов (компактно)
        for k, v in self.calculation_results.items():
            lbl = ctk.CTkLabel(self.results_container, text=f"{k}: {v}")
            lbl.pack(anchor="w", padx=6, pady=2)

    def clear_parameters(self):
        for ent in self.input_entries.values():
            ent.delete(0, "end")
        for w in self.results_container.winfo_children():
            w.destroy()
        self.file_status_label.configure(text="Файл не сохранён", text_color="gray")
        self.initial_message = ctk.CTkLabel(self.results_container,
                                            text="Введите параметры и нажмите 'Рассчитать'",
                                            text_color="gray")
        self.initial_message.pack(pady=20)
        self.calculation_results = None
        self.current_file_path = None

    # ---------------- JSON SAVE / LOAD ----------------
    def save_calculation(self):
        try:
            save_data = {
                "metadata": {
                    "sensor_type": self.selected_sensor,
                    "scheme_type": self.selected_scheme,
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "user_parameters": {k: float(v.get()) if v.get() != "" else None for k, v in self.input_entries.items()},
                "calculation_results": self.calculation_results
            }
            if not self.current_file_path:
                path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
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

            # загрузка результатов, если есть
            if data.get("calculation_results"):
                self.calculation_results = data["calculation_results"]
                self.update_results_display()

            self.current_file_path = path
            self.file_status_label.configure(text=f"Загружено: {os.path.basename(path)}", text_color="blue")
            messagebox.showinfo("Успех", f"Файл загружен:\n{path}")

            # перерисовка схемы по загруженным параметрам
            try:
                self.update_parameters_from_input(skip_validation=True)
            except Exception:
                pass
            self.draw_zip_scheme()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
