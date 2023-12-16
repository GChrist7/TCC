from django.shortcuts import render
from django.http import HttpResponse

import paho.mqtt.client as mqtt
from django.conf import settings

import math
import numpy as np
from sklearn.linear_model import LinearRegression

# Auxiliar Functions

def get_inputs(request):
    Up=[]
    Down=[]
    Up.append(float(request.POST.get("Up8")))
    Up.append(float(request.POST.get("Up7")))
    Up.append(float(request.POST.get("Up6")))
    Up.append(float(request.POST.get("Up5")))
    Down.append(float(request.POST.get("Dw8")))
    if(Down[0] > 0):
        Down[0] = Down[0] * (-1)
    Down.append(float(request.POST.get("Dw7")))
    if(Down[1] > 0):
        Down[1] = Down[1] * (-1)
    Down.append(float(request.POST.get("Dw6")))
    if(Down[2] > 0):
        Down[2] = Down[2] * (-1)
    Down.append(float(request.POST.get("Dw5")))
    if(Down[3] > 0):
        Down[3] = Down[3] * (-1)
    return Up, Down

#Funções dos Cálculos

def Degree_calcultation(Up, Down):
    Upd = []
    for i in Up:
        calc = round(math.degrees(math.asin( i / 63)), 3)
        Upd.append(calc)
    Downd = []
    for i in Down:
        calc = round(math.degrees(math.asin( i / 63)), 3)
        Downd.append(calc)
    return Upd, Downd

def Make_previsions(output):
    #Cycle 1
    test_output_up = np.array(output[0:4]).reshape(-1,1)
    index_output_up = np.array([8,7,6,5]).reshape(-1,1)

    test_output_dw = np.array(output[4:9]).reshape(-1,1)
    index_output_dw = np.array([-5,-6,-7,-8]).reshape(-1,1)

    modelo_up = LinearRegression()
    modelo_up.fit(index_output_up, test_output_up)

    modelo_dw = LinearRegression()
    modelo_dw.fit(index_output_dw, test_output_dw)

    a_coef_up = modelo_up.coef_
    l_coef_up = modelo_up.intercept_

    a_coef_dw = modelo_dw.coef_
    l_coef_dw = modelo_dw.intercept_

    x_plot_up = np.array([0,1,2,3,4,5,6,7,8]).reshape(-1,1)
    y_plot_up = np.array([l_coef_up + a_coef_up * x_plot_up]).reshape(-1,1)

    x_plot_dw = np.array([0,-1,-2,-3,-4,-5,-6,-7,-8]).reshape(-1,1)
    y_plot_dw = np.array([l_coef_dw + a_coef_dw * x_plot_dw]).reshape(-1,1)

    load_4uf = 4
    load_3uf = 3
    load_2uf = 2
    load_1uf = 1
    no_load_uf = 0

    #4uf
    off_download_4 = round(float(l_coef_up + a_coef_up * load_4uf),4)
    down_4 = "%.4f" % off_download_4 
    off_loading_4 = round(float(l_coef_dw + a_coef_dw * (-load_4uf)),4)
    load_4 = "%.4f" % off_loading_4 

    #3uf
    off_download_3 = round(float(l_coef_up + a_coef_up * load_3uf),4)
    down_3 = "%.4f" % off_download_3 
    off_loading_3 = round(float(l_coef_dw + a_coef_dw * (-load_3uf)),4)
    load_3 = "%.4f" % off_loading_3 

    #2uf
    off_download_2 = round(float(l_coef_up + a_coef_up * load_2uf),4)
    down_2 = "%.4f" % off_download_2 
    off_loading_2 = round(float(l_coef_dw + a_coef_dw * (-load_2uf)),4)
    load_2 = "%.4f" % off_loading_2 

    #1uf
    off_download_1 = round(float(l_coef_up + a_coef_up * load_1uf),4)
    down_1 = "%.4f" % off_download_1 
    off_loading_1 = round(float(l_coef_dw + a_coef_dw * (-load_1uf)),4)
    load_1 = "%.4f" % off_loading_1 

    #0uf
    off_download = round(float(l_coef_up + a_coef_up * no_load_uf),4)
    down = "%.4f" % off_download #Previsões
    off_loading = round(float(l_coef_dw + a_coef_dw * no_load_uf),4)
    load = "%.4f" % off_loading #Previsões

    previsions = [off_download_4, off_loading_4, off_download_3, off_loading_3, off_download_2, off_loading_2, off_download_1, off_loading_1, off_download, off_loading]

    return previsions


def Backlash(prevs):
    backlash_string_1 = ("Resultado obtido pelo cálculo: |Deslocamento 0 uf Up - Deslocamento 0 uf Down|")
    backlash_string_2 = ("Result: Test Not Accepted (Outside the Backlash Limits)")
    backlash_string_3 = ("Backlash (Degree): Invalid")

    backlash = abs(prevs[8] - prevs[9])

    backlash_num = "%.4f" % backlash
    if(backlash <= 0.57):
        backlash_string = backlash_string_1
    else:
        backlash_string = backlash_string_2


    return backlash_num, backlash_string,

# Create your views here.

def index(request):
    if(request.method == 'POST'):
        Up=[]
        Down=[]
        Up, Down = get_inputs(request)

        Upd=[]
        Downd=[]
        Upd, Downd = Degree_calcultation(Up, Down)

        input = (Upd[0], Upd[1], Upd[2], Upd[3], Downd[3], Downd[2], Downd[1], Downd[0])
        previsions = []
        previsions = Make_previsions(input)

        backlash_num, backlash_string = Backlash(previsions)

        return render(request, 'pages/profile.html', {
                                                    "Degree_Up8": Upd[0],
                                                    "Degree_Up7": Upd[1],
                                                    "Degree_Up6": Upd[2],
                                                    "Degree_Up5": Upd[3],
                                                    "Degree_Dw8": Downd[0],
                                                    "Degree_Dw7": Downd[1],
                                                    "Degree_Dw6": Downd[2],
                                                    "Degree_Dw5": Downd[3],
                                                    "prev_up4": previsions[0],
                                                    "prev_dw4": previsions[1],
                                                    "prev_up3": previsions[2],
                                                    "prev_dw3": previsions[3],
                                                    "prev_up2": previsions[4],
                                                    "prev_dw2": previsions[5],
                                                    "prev_up1": previsions[6],
                                                    "prev_dw1": previsions[7],
                                                    "prev_up": previsions[8],
                                                    "prev_dw": previsions[9],
                                                    "backlash_num": backlash_num,
                                                    "backlash_string": backlash_string})
    else:
        return render(request, 'pages/index.html')