import numpy as np
import math as m
from core.geometry import *

def calc_N (h1,L_c,S_c): #Коэффициент размагничивания магнитопровода

    v = h1/L_c
    alpha = 0.5* L_c * m.sqrt(np.pi/S_c)

    chi = 1 + 0.211* v**-1.116
    theta = 6.855-8.074*alpha**0.1353

    N = 4 * np.pi * chi* np.exp(theta)
    return N

def calc_R_mC(L_c,S_c,N,mu_c,mu_0): #Полное магнитное сопротивление "сатльной" части магнитопровода

    mu_c_otn = mu_c/mu_0
    mu_c_full = mu_c_otn / (1 + (N/4*np.pi)*(mu_c_otn - 1))

    R_mC = L_c/mu_0*mu_c_full*S_c
    return R_mC

def calc_R_mb(l0,mu_0,S_B,x): #Завимисомть сопротивления магнитопровода и перемещение якоря

    k_B = 1/l0
    R_B0 = 2*l0/mu_0*S_B

    R_mb = R_B0*(1-k_B*x)

    return R_mb, k_B

def calc_Z_x(x, f_p,R_mC, R_B0, w, k_B, eta): #Полное электрическое сопротивление катушки ЗИП

    z_0 = 2*np.pi*f_p/m.sqrt(1-eta**2) * w**2/(R_mC+R_B0)
    k_x = k_B*(R_B0/(R_mC+R_B0))

    Z_x = z_0/(1-k_x*x)

    return Z_x

def calc_gamma (k_x,xv): #Максимальная приведенная погрешность
    q = k_x*xv
    gamma = q/2*(1+m.sqrt((1-q**2)))

    return gamma,q

def calc_d_z (q):
    d_z = q/m.sqrt(1-q**2)
    return d_z

def calc_w_0(d_n): #Удельное число витков катушки
    w_0 = (4/np.pi*d_n**2)*(0.375+(3.935*d_n/(1+12.448*d_n)))
    return w_0

def calc_w(w_0,S_ok): #Число витков катушки
    w = w_0*S_ok
    return w

def calc_R_k(R_cp,w,d_n, p_n):
    R_k = 8*p_n*(R_cp*w/d_n**2)
    return R_k

def calc_eta(R_k,z_0,d_z):
    eta = R_k/z_0(1-d_z)
    return eta

def calc_f_p(z_0,w,eta,R_mC,R_B0):
    R_m0 = R_mC+R_B0
    f_p = (z_0*R_m0/2*np.pi*w**2)*m.sqrt(1-eta**2)
    return f_p

