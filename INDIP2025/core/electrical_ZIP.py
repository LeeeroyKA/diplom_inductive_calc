import numpy as np
import math as m
from core import geometry_ZIP,validation

def calc_R_B(l0,x,mu_0,S_B):
    l_b5 = l0 - x
    l_b6 = l0 - x
    L_b = l_b5+l_b6
    R_B = L_b/(mu_0*S_B)

    print(f"Сопротивление воздушной части магнитопровода  R_B... {R_B}")

    return R_B


def calc_N (h2,L_c,S_c): #Коэффициент размагничивания магнитопровода

    v = 0.9*h2/L_c
    alpha = 0.5* L_c * m.sqrt(np.pi/S_c)

    chi = 1 + 0.211* v**-1.116
    theta = 6.855-8.074*alpha**0.1353

    N = 4 * np.pi * chi* np.exp(theta)

    print(f"Коэффициент размагничивания магнитопровода N... {N}")

    return N

def calc_R_mC(L_c,S_c,N,mu_c,mu_0): #Полное магнитное сопротивление "стальной" части магнитопровода

    mu_c_otn = mu_c/mu_0
    mu_c_full = mu_c_otn / (1 + (N/4*np.pi)*(mu_c_otn - 1))

    R_mC = L_c/mu_0*mu_c_full*S_c

    print(f"Полное магнитное сопротивление стальной части магнитопровода R_mC... {R_mC}")

    return R_mC

def calc_R_mb(l0,mu_0,S_B,x): #Завимисомть сопротивления магнитопровода и перемещение якоря

    k_B = 1/l0
    R_B0 = 2*l0/mu_0*S_B

    R_mb = R_B0*(1-k_B*x)

    print(f"Завимисомть сопротивления магнитопровода и перемещение якоря R_mb, k_B... {R_mb, k_B}")

    return R_mb, k_B,R_B0

def calc_k_x(R_mC, R_B0, k_B): #Относительный коэффициент чувствительности

    k_x = k_B*(R_B0/(R_mC+R_B0))

    print(f"Относительный коэффициент чувствительности k_x... {k_x}")

    return k_x

def calc_z_0(f_p,R_mC, R_B0, w,eta): #Начальное электрическое сопротивление катушки

    z_0 = 2*np.pi*f_p/m.sqrt(1-eta**2) * w**2/(R_mC+R_B0)

    print(f"Начальное электрическое сопротивление катушки z_0... {z_0}")

    return z_0

def calc_Z_x(x,z_0,k_x): #Полное электрическое сопротивление катушки ЗИП

    Z_x = z_0/(1-k_x*x)

    print(f"Полное электрическое сопротивление катушки ЗИП Z_x... {Z_x}")

    return Z_x

def calc_gamma (k_x,xv): #Максимальная приведенная погрешность
    q = k_x*xv
    gamma = q/2*(1+m.sqrt((1-q**2)))

    print(f"Максимальная приведенная погрешность gamma... {gamma}")

    return gamma,q

def calc_gamma_pi (gamma):
    gamma_pi = 4*gamma**2/((1+4*gamma**2)**4) * (3 + m.sqrt( 144*gamma**4 + 64* gamma **2 + 9/ (1+4*gamma**2)**2))
    print (gamma_pi)
    return gamma_pi

def calc_d_z (q):
    d_z = q/m.sqrt(1-q**2)
    print(f"Максимальная приведенная погрешность d_z... {d_z}")
    return d_z

def calc_w_0(d_n): #Удельное число витков катушки
    w_0 = (4/np.pi*d_n**2)*(0.375+(3.935*d_n/(1+12.448*d_n)))
    print(f"Удельное число витков катушки w_0... {w_0}")
    return w_0

def calc_w(w_0,S_ok): #Число витков катушки
    w = w_0*S_ok
    print(f"Число витков катушки w... {w}")
    return w

def calc_R_k(R_cp,d_n,w, p_n): #Активное сопротивление катушки (Ошибка в коде? Разные формулы у разных людей)
    R_k = 8*p_n*(R_cp*w/d_n**2)
    print(f"Число витков катушки R_k... {R_k}")
    return R_k

def calc_eta(R_k,z_0_eta,d_z): #Доля активного сопротивление катушки
    eta = R_k/(z_0_eta*(1-d_z))
    print(f"Доля активного сопротивление катушки eta... {eta}")
    return eta

def calc_f_p(z_0,w,eta,R_mC,R_B0): #Частота напряжения питания
    R_m0 = R_mC+R_B0
    f_p = (z_0*R_m0/2*np.pi*w**2)*m.sqrt(1-eta**2)
    print(f"Частота напряжения питания f_p... {f_p}")
    return f_p

