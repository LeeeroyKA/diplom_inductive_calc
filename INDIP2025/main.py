import math as m
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import customtkinter as ctk

from models.sensor_zip import ZIPSensor
from core import geometry_ZIP, electrical_ZIP
from models.sensor_pip import PIPSensor
from IO.GUI import InputWindow
from IO.zip_window import ZIPWindow
from IO.sip_window import SIPWindow
from IO.pip_window import PIPWindow



def main():
    """Главная функция приложения"""
    # Создание и запуск GUI для ввода параметров
    input_app = InputWindow()
    input_app.mainloop()  # Блокируется до закрытия окна

    # Проверяем, было ли окно закрыто через кнопку "Начать расчет"
    if hasattr(input_app, 'completed') and input_app.completed:
        params = input_app.calculation_results

        # Присвоение переменным из GUI
        xv = params['xv']
        d_zT_min = params['d_zT_min']
        selected_sensor = params['selected_sensor']
        selected_scheme = params['selected_scheme']

        print(f"Получены параметры из GUI:")
        print(f"Диапазон: {xv}")
        print(f"Погрешность: {d_zT_min}%")
        print(f"Датчик: {selected_sensor}")
        print(f"Схема: {selected_scheme}")
        print('')


        mu_0 = 4 * np.pi * 10 ** -10


        # Выбор и создание датчика в зависимости от выбора пользователя
        if selected_sensor == "ДЗИП":
            print("Создаем модель датчика ЗИП...")
            result_window = ZIPWindow(input_app, params)
            #sensor = ZIPSensor(D1, D2, d1, d2, h1, h2, h3, l0, z0, d_n, xv, d_zT_min, eta_max, x, K_kp, p_n, mu_0, mu_c, z_0_eta)
        elif selected_sensor == "ДПИП":
            print("Создаем модель датчика ПИП...")
            result_window = SIPWindow(input_app, params)
            #sensor = PIPSensor(D1, D2, d1, d2, h1, h2, h3, l0, z0, d_n, xv, d_zT_min, eta_max, x, K_kp, p_n, mu_0, mu_c, z_0_eta)
        else:
            print("Выбран ДСИП - функционал в разработке")
            result_window = PIPWindow(input_app, params)
            return

        # Запуск расчета
        print("Запускаем расчет параметров...")
        #result = sensor.calc()


    else:
        print("Окно было закрыто без расчета")



if __name__ == "__main__":
    main()