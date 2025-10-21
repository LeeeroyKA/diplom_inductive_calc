class ZIPSensor:
    def __init__(self, D1, D2, d1, d2, h1, h2, h3, l0, z0, d_n, xv):
        # Геометрические параметры
        self.D1 = D1  # внешний диаметр сердечника
        self.D2 = D2  # внешний диаметр катушки
        self.d1 = d1  # диаметр технического отверстия
        self.d2 = d2  # внутренний диаметр катушки
        self.h1 = h1  # высота катушки
        self.h2 = h2  # высота сердечника
        self.h3 = h3  # толщина якоря
        self.l0 = l0  # начальный воздушный зазор

        # Диапозон измерения
        self.xv = xv    # Максимальный диапозон измерения

        # Электрические параметры
        self.z0 = z0  # начальное сопротивление
        self.d_n = d_n  # диаметр провода


        self.results = {}

        self.w = None
        self.R_k = None
        self.etf = None
        self.d_z = None

    def get_params(self):
        return {'D1' : self.D1, 'D2' : self.D2, 'd1' : self.d1, 'd2': self.d2,
                'h1' : self.h1, 'h2' : self.h2, 'h3' : self.h3, 'l0' : self.l0,
                'xv' : self.xv, 'z0' : self.z0, 'd_n' : self.d_n,}

    def update_result(self, result):
        for key, value in result.items():
            setattr(self, key, value)



