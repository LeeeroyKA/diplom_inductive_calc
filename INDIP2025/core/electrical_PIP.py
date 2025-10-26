from math import log10

import numpy as np
import math as m
from core import geometry_PIP,validation

def calc_N (L_c,h2,S_c):
    v = h2/L_c
    alpha = 0.5*L_c*m.sqrt(np.pi/S_c)

    chi = 1 + 0.211*v**-1.116
    theta = 6.855 - 8.074*alpha**0.1353

    N = 4*np.pi*chi*np.exp(theta)

    print(f"Коэффициент размагничивания магнитопровода N = {N}")

    return N

def calc_R_mC(h_c,N,mu_c,mu_0,a1,a2,a3,d1,d2):

    mu_c_otn = mu_c / mu_0
    mu_c_full = mu_c_otn / (1 + (N / 4 * np.pi) * (mu_c_otn - 1))

    R_mC = (1/mu_0*mu_c_full)*(a1+a2+a3+(4*h_c/np.pi*((d1**2)-(d2**2))))

    print(f"Полное магнитное сопротивление стальной части магнитопровода R_mC = {R_mC}")

    return R_mC

def calc_R_B0(mu_0,H,l0,d,d1):

    R_B0 = (1/2*np.pi*mu_0)*((H+l0)/H*l0)*np.log(d/d1)

    print(f"Начальное магнитное сопротивление воздушных зазоров R_B0 = {R_B0}")
    return R_B0


def calc_z_x(l0,H, R_B0,R_mC,x,z0):

    beta_zx = l0/(l0+H)
    gamma = R_B0/R_mC
    k_x = 1/l0
    alpha_zx = (1+beta_zx*gamma)/(1+gamma)

    Z_x = z0*((1+k_x*x)/(1+alpha_zx*k_x*x))

    print(f"Полное электрическое сопротивление  Z_x = {Z_x}")

    return Z_x,alpha_zx

def calc_gamma_pip(k_x,xv,alpha_zx):

    q = k_x*xv
    gamma_pip = (alpha_zx*q)/2*(1+m.sqrt(1-(alpha_zx*q)**2))

    print(f"Максимальная приведенная погрешность от нелинейности статической характеристики преобразователя gamma_pip = {gamma_pip}")
    return gamma_pip

def calc_d_z(gamma_pip,dz):

    alpha_dz = (4*gamma_pip/(1+4*gamma_pip**2))*((1+(4*gamma_pip**2)+2*dz*gamma_pip*(1-4*gamma_pip**2)/(4*gamma_pip+ dz*(1-4*gamma_pip**2))))
    q = (4*gamma_pip + dz*(1-4*gamma_pip**2))/(1+4*gamma_pip**2+2*dz*gamma_pip*(1-4*gamma_pip**2))\

    dz = (1 - alpha_dz) * alpha_dz * q / (1 - (alpha_dz * q) ** 2 - (1 - alpha_dz) * m.sqrt(1 - (alpha_dz * q) ** 2))

    print( f"Относительная девиация сопротивления катушки ПИП dz = {dz}")
    return dz

def calc_R_k(ro_n,R_cp,w,d_n):

    R_k = 8*ro_n*(R_cp*w/d_n**2)
    print(f"Активное сопротивление катушки R_k = {R_k}")

    return R_k

def calc_etta(z0,d_z,R_k):

    etta = R_k/(z0*(1-d_z))

    print(f"Доля активного сопротивления катушки etta = {etta}")

    return etta

def calc_f_p(R_mC, R_B0,etta,w,z0):

    R_m0 = R_mC+ R_B0

    f_p = (z0*R_m0/2*np.pi*w**2)*m.sqrt(1-etta**2)

    print(f"Частота напряжения питания f_p = {f_p}")

    return f_p

