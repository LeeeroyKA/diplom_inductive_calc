import sys

import numpy as np
import math as m
from core import electrical_ZIP,geometry_ZIP

def valid_start_values(d_zT_min,eta_max,l0,xv):
    stop = 0
    if l0>xv:
        stop = 0
    else:
        print("Начальный воздушный зазор меньше максимума диапозона измерений ")
        stop = 1
    return stop