from core import geometry_PIP, electrical_PIP


class PIPSensor:
    def __init__(self, D1, D2, d1, d2, h1, h2, h3, l0, z0, d_n, xv, d_zT_min, eta_max, x, K_kp, p_n, mu_0, mu_c,z_0_eta):
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

        # Общие параметры
        self.d_zT_min = d_zT_min
        self.eta_max = eta_max
        self.x = x
        self.K_kp = K_kp
        self.p_n = p_n
        self.mu_0 = mu_0
        self.mu_c = mu_c
        self.z_0_eta = z_0_eta

        if self.l0 < self.xv:
            print("Верхняя граница диапозона измерений меньше")

    def calc(self):
        S_B = geometry_PIP.calc_S_B(self.D1, self.D2, self.d2, self.d1)
        L_cd, l_c3, l_c2, l_c1 = geometry_PIP.calc_L_cd(self.h1, self.h2, self.D1, self.D2, self.d1, self.d2)
        S_cd, a1, a2, a3 = geometry_PIP.calc_S_cd(L_cd, self.h1, self.h2, self.D1, self.D2, self.d1, self.d2)
        S_y, L_y = geometry_PIP.calс_S_yakor(l_c3, self.h3, self.D1, self.D2, self.d1, self.d2)
        L_c, S_c = geometry_PIP.calc_L_S_magnit(L_y, L_cd, S_cd, S_y)
        S_ok = geometry_PIP.calc_S_ok(self.D2, self.d2, self.h1, self.K_kp)
        R_cp = geometry_PIP.calc_R_cp(self.D2, self.d2)

        # 2. Электрические расчеты
        N = electrical_PIP.calc_N(self.h1, L_c, S_c)
        R_mC = electrical_PIP.calc_R_mC(L_c, S_c, N, self.mu_c, self.mu_0)
        R_mb, k_B , R_B0 = electrical_PIP.calc_R_mb(self.l0, self.mu_0, S_B, 0)  # x=0 для начального положения
        w_0 = electrical_PIP.calc_w_0(self.d_n)
        w = electrical_PIP.calc_w(w_0, S_ok)
        R_k = electrical_PIP.calc_R_k(R_cp,self.d_n, self.p_n,w)

        R_B = electrical_PIP.calc_R_B(self.l0, self.mu_0, S_B, self.x)

        k_x = electrical_PIP.calc_k_x(R_mC, R_B0, k_B)
        gamma, q = electrical_PIP.calc_gamma(k_x, self.xv)
        d_z = electrical_PIP.calc_d_z(q)

        eta = electrical_PIP.calc_eta(R_k, self.z_0_eta, d_z)

        f_p = electrical_PIP.calc_f_p(self.z_0_eta,w,eta,R_mC,R_B0)

        z_0 = electrical_PIP.calc_z_0(f_p, R_mC, R_B0, w, eta)
        x = 0
        gamma_pi = electrical_PIP.calc_gamma_pi(gamma)
        Z_x= electrical_PIP.calc_Z_x(z_0,k_x,x)

        # Сохраняем результаты
        results = {
            'S_B': S_B, 'L_cd': L_cd, 'l_c3': l_c3, 'S_cd': S_cd,
            'S_y': S_y, 'L_y': L_y, 'L_c': L_c, 'S_c': S_c,
            'S_ok': S_ok, 'R_cp': R_cp, 'N': N, 'R_mC': R_mC,
            'R_mb': R_mb, 'k_B': k_B, 'w_0': w_0, 'w': w,
            'R_k': R_k, 'f_p': f_p, 'eta': eta, 'gamma': gamma,
            'q': q, 'd_z': d_z, 'Z_x': Z_x
        }

        self.update_result(results)
        return results
