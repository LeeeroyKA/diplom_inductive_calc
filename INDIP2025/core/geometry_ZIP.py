import numpy as np
import math as m
from core import electrical_ZIP,validation

def calc_S_B(D1,D2,d2,d1): #Площадь сечения воздушной части магнитопровода
    S_e5 = np.pi/4 * (D1**2 - D2**2) #Площадь сечения на участке 5
    S_e6 = np.pi/4 * (d2**2 - d1**2) #Площадь сечения на участке 6

    print(f"Производим расчет:")
    print(f"Коэффициент S_e5 ... {round(S_e5,3)}")
    print(f"Коэффициент S_e6 ... {round(S_e6,3)}")
    S_B = 2*(S_e5*S_e6/(S_e5 + S_e6)) #Площадь сечения воздушной части магнитопровода
    print(f"Площади сечения воздушной части магнитопровода S_B... {round(S_B,3)}" )
    return S_B

def calc_L_cd(h1,h2,D1,D2,d1,d2): #Длина сечения сердечника

    l_c1 = (h1+h2)/2
    l_c2 = l_c1
    l_c3 = 0.5*(((D1+D2)/2) - ((d1+d2)/2))

    L_cd = l_c1+l_c2+l_c3

    print(f"Коэффициент l_c1 ... {round(l_c1,3)}")
    print(f"Коэффициент l_c2 ... {round(l_c2,3)}")
    print(f"Коэффициент l_c3 ... {round(l_c3,3)}")
    print(f"Длины сечения сердечника L_cd... {round(L_cd,3)}")
    return L_cd, l_c3, l_c2, l_c1

def calc_S_cd(L_cd,h1,h2,D1,D2,d1,d2): #Площадь сечения сердечника

    a1 = 2*(h1+h2)/(np.pi*(D1**2 - D2**2))
    a2 = 2*(h1+h2)/(np.pi*(d2**2 - d1**2))
    a3 = 1/(2*np.pi*(h2-h1))* np.log((D1+D2)/(d1+d2))

    S_cd = L_cd / (a1 + a2 + a3)

    print(f"Коэффициент a1 ... {round(a1,3)}")
    print(f"Коэффициент a2 ... {round(a2,3)}")
    print(f"Коэффициент a3 ... {round(a3,3)}")
    print(f"Площади сечения сердечника S_cd... {round(S_cd,3)}")
    return S_cd, a1, a2, a3

def calc_S_yakor(l_c3,h3, D1, D2, d1, d2): #Площадь сечения и длина якоря

    L_y = l_c3
    S_y = 2*np.pi*h3*L_y/(np.log((D1+D2)/(d1+d2)))

    print(f"Площади сечения якоря S_y... {round(S_y,3)}")
    print(f"Длина якоря L_y... {round(L_y,3)}")
    return S_y,L_y

def calc_L_S_magnit(L_y,L_cd,S_cd,S_y): #Длина и площадь магнитопровода

    L_c = L_cd + L_y
    S_c = L_c/((L_cd/S_cd)+(L_y/S_y))

    print(f"Длина магнитопровода L_c.. {round(L_c,3)}")
    print(f"Площадь магнитопровода S_c... {round(S_c,3)}")
    return L_c, S_c

def calc_S_ok(D2,d2,h1,K_kp): #Площадь окна катушки
    S_ok = 0.5*(D2-d2)*h1*K_kp
    print(f"Площади окна катушки S_ok... {round(S_ok,3)}")
    return S_ok

def calc_R_cp(D2,d1): #Средний радиус катушки ВЕЗДЕ РАЗНЫЕ ФОРМУЛЫ
    R_cp = 0.25*(D2-d1)
    print(f"Среднего радиуса катушки R_cp... {R_cp}")
    return R_cp





