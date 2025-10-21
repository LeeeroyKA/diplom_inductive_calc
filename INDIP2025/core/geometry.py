import numpy as np
import math as m

def calc_S_B(D1,D2,d2,d1): #Площадь сечения воздушной части магнитопровода
    S_e5 = np.pi/4 * (D1**2 - D2**2) #Площадь сечения на участке 5
    S_e6 = np.pi/4 * (d2**2 - d1**2) #Площадь сечения на участке 6

    S_B = 2*(S_e5*S_e6/(S_e5 + S_e6)) #Площадь сечения воздушной части магнитопровода
    return S_B

def calc_L_cd(h1,h2,D1,D2,d1,d2): #Длина сечения сердечника

    l_c1 = (h1+h2)/2
    l_c2 = l_c1
    l_c3 = 0.5*((D1+D2)/2 + (d1+d2)/2)

    L_cd = l_c1+l_c2+l_c3
    return L_cd, l_c3, l_c2, l_c1

def calc_S_cd(L_cd,h1,h2,D1,D2,d1,d2): #Площадь сечения сердечника

    a1 = 2*(h1+h2)/np.pi*(D1**2 - D2**2)
    a2 = 2*(h1+h2)/np.pi*(d2**2 - d1**2)
    a3 = 1/(2*np.pi*(h2-h1))* np.log((D1+D2)/(d1+d2))

    S_cd = L_cd / (a1 + a2 + a3)

    return S_cd, a1, a2, a3

def calс_S_yakor(l_c3, D1, D2, d1, d2): #Площадь сечения и длина якоря

    L_y = l_c3
    S_y = 2*np.pi*L_y/ (np.log((D1+D2)/(d1+d2)))

    return S_y,L_y

def calc_L_S_magnit(L_y,L_cd,S_cd,S_y): #Длина и площадь магнитопровода

    L_c = L_cd + L_y
    S_c = L_c/((L_cd/S_cd)+(L_y/S_y))

    return L_c, S_c

def calc_S_ok(D2,d2,h1,K_kp): #Площадь окна катушки
    S_ok = 0.5*(D2-d2)*h1*K_kp
    return S_ok

def calc_R_cp(D2,d2): #Средний радиус катушки
    R_cp = (D2+d2)/4
    return R_cp





