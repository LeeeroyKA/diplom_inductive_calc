import math as m
import numpy as np
import scipy as sp
import flet as ft
import matplotlib as mpl
import matplotlib.pyplot as plt

from models.sensor_zip import ZIPSensor
from core import geometry,electrical

xv = 0.03
d_zT_min = 3
eta_max = 5

x=0.003
x_start = -1*xv
#while x_start <= 0.03:
    #x.append(x_start)
    #x_start = x_start -

K_kp = 0.7
p_n = 17.5*10**-6 #Удельное сопротивление меди



mu_c = 3000
mu_0 = 4*np.pi*10**-10


z0 = 2000
z_0_eta = 2000
d_n = 0.1

d1 = 3
d2 = 5
D1 = 14
D2 = 13.5
h1 = 3
h2 = 3.5
h3 = 1
l0 = 0.035


print("Создаем модель датчика ЗИП...")
ZIP = ZIPSensor(D1, D2, d1,d2, h1, h2, h3, l0, z0, d_n,xv, d_zT_min, eta_max, x, K_kp, p_n, mu_0, mu_c,z_0_eta)
result = ZIP.calc()
print("Запускаем расчет параметров...")
print (ZIP)
