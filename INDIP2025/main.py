import math as m
import numpy as np
import scipy as sp
import flet as ft
import matplotlib as mpl
import matplotlib.pyplot as plt

from models.sensor_zip import ZIPSensor
from core import geometry_ZIP,electrical_ZIP
# Начальные данные для ЗИП
xv = 0.5
d_zT_min = 10
eta_max = 5

x=0.003
x_start = -1*xv

K_kp = 1
p_n = 17.5*10**-6 #Удельное сопротивление меди

mu_c = 3000
mu_0 = 4*np.pi*10**-10

z0 = 1000
z_0_eta = 2000
d_n = 0.1

d1 = 7
d2 = 9
D1 = 47
D2 = 27
h1 = 10
h2 = 15
h3 = 5
l0 = 0.055

# Начальные данные для ПИП


print("Создаем модель датчика ЗИП...")
ZIP = ZIPSensor(D1, D2, d1,d2, h1, h2, h3, l0, z0, d_n,xv, d_zT_min, eta_max, x, K_kp, p_n, mu_0, mu_c,z_0_eta)
result = ZIP.calc()
print("Запускаем расчет параметров...")
print (ZIP)
