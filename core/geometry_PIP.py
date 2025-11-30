import numpy as np
import math as m
from core import electrical_PIP,validation

def calc_S_B (h3,h2,t_B,d1,l0):

    d = d1 + 2*t_B
    H = h3-h2

    S_B5 = (2*np.pi*H*t_B)/np.log(d/(d-2*t_B))
    S_B6 = (2*np.pi*l0*t_B)/np.log(d/(d-2*t_B))

    S_B = 2*((S_B5 * S_B6)/(S_B5+S_B6))

    print(f"Площадь сечения воздушной части магнитопровода S_B = {S_B}")
    return S_B, H , d

def calc_L_cd(D1,D2,H,h2,l0,d):

    h_c = h2 + 0.5 * (H + l0)
    D = 0.5*(D1+D2)
    L_cd = D - d + h_c

    print(f"Длина сечения сердечника L_cd = {L_cd}")

    return L_cd,D,h_c

def calc_S_cd(h_c,D1,D2,H,D,d,l0,L_cd):

    a1 = (h_c/np.pi*(D1**2 - D2**2))
    a2 = 1/(2*np.pi*H)*np.log(D/d)
    a3 = 1/(2*np.pi*l0)*np.log(D/d)

    S_cd = L_cd/(a1 + a2 + a3)
    print(f"Площадь сечения сердечника S_cd = {S_cd}")

    return S_cd, a1, a2, a3

def calc_S_ya(h_c,d1,d2):
    L_y = h_c
    S_y = 0.25*(np.pi*(d1**2 - d2**2))

    print(f"Длина якоря L_y = {L_y}")
    print(f"Площадь якоря S_y = {S_y}")

    return S_y, L_y

def calc_S_c(L_cd,L_y,S_cd,S_y):

    L_c = L_cd + L_y
    S_c = L_c/(L_cd/S_cd)+(L_y/S_y)

    print(f"Длина сечения магнитопровода L_c = {L_c}")
    print(f"Площадь сечения магнитопровода S_c = {S_c}")

    return S_c,L_c

def calc_S_ok(D2,d,h2,K_kp):

     S_ok = 0.4*(D2 - d) * h2 * K_kp

     print(f"Площадь окна катушки S_ok = {S_ok}")

     R_cp = 0.25*(D2+d)

     print(f"Средний радиус катушки R_cp = {R_cp}")

     return S_ok,R_cp

def calc_w0(d_n):

    w0 = (4/np.pi*d_n**2)*(0.375+(3.935*d_n/(1+(12.448*d_n))))

    print(f"Средний радиус катушки w0 = {w0}")
    return w0

def calc_w(w0,S_ok):

    w = w0*S_ok
    print(f"Число витков катушки w = {w}")

    return w

