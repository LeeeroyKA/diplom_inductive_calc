import customtkinter as ctk


class SIPWindow(ctk.CTkToplevel):
    def __init__(self, parent, params):
        super().__init__()
        self.title("ДСИП - Результаты расчета")
        self.geometry("1000x700")
        self.params = params
        self.create_tabs()

    def create_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.scheme_tab = self.tabview.add("Scheme")
        self.results_tab = self.tabview.add("Results")
        self.params_tab = self.tabview.add("Start Params")

        self.setup_scheme_tab()
        self.setup_results_tab()
        self.setup_params_tab()

    def setup_scheme_tab(self):
        label = ctk.CTkLabel(self.scheme_tab, text="Схема ДСИП", font=("Arial", 16))
        label.pack(pady=20)

    def setup_results_tab(self):
        label = ctk.CTkLabel(self.results_tab, text="Результаты ДСИП", font=("Arial", 16))
        label.pack(pady=20)

    def setup_params_tab(self):
        label = ctk.CTkLabel(self.params_tab, text="Параметры ДСИП", font=("Arial", 16))
        label.pack(pady=20)