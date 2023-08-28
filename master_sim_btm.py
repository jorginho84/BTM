# -*- coding: utf-8 -*-
"""
This script is to simulate data

Created on Tue Jun 20 12:52:51 2023

@author: Patricio De Araya
"""

import numpy as np
import pandas as pd
import pickle
import tracemalloc
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
import matplotlib.pyplot as plt
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1")
import utility_btm as util
import parameters_btm as parameters
import simdata_btm as sd
#import estimate as est
#import estimate_2 as est_2
#import estimate_3 as est_3
#import between
#import random
#import xlsxwriter
from openpyxl import Workbook 
from openpyxl import load_workbook
import time

#### **** Parameters **** ####

gammas_x = [0.1,0.2]
alphas_es = [0.75, 0.25, 98, 6320]
delta = [5, 8, 3]

mar_workload = np.load('mar_work_model.npy', allow_pickle=True)
dmar_workload = np.load('dmar_work_model.npy', allow_pickle=True)
dont_workload = np.load('dont_work_model.npy', allow_pickle=True)

s_info = 0.5

sigma_foc_score = np.random.randint(5,10,(3000))

######################## **** **** ########################

print(mar_workload[0][3])


shock_test_n = np.random.randn(3)

a = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
b = np.array([0.5, 0.5, 0.5])

c = a.dot(b)
#y = np.log(c) + np.log(shock_test_n)
educ = np.random.randint(5,13,(3000))
age = np.random.randint(25,59,(3000))
data_reg_btm_v1 = {'educ': educ, 'age': age}
data_reg_btm = pd.DataFrame(data_reg_btm_v1)
X = data_reg_btm.values



#creo variables que estén tabla, también betas en log

year = np.random.randint(2012,2016,(3000))
psfe = np.random.randint(90,120,(3000))
N = np.size(psfe)
ecivil = np.random.randint(0,2,(3000))
children = np.random.randint(0,4,(3000))
#shock_information = np.random.randint(0,2,(3000))
work_d = np.random.randint(0,2,(3000))
btm_d = np.random.randint(0,2,(3000))



param0 = parameters.Parameters(gammas_x,mar_workload,dmar_workload,dont_workload,s_info,delta,
                               sigma_foc_score)

model = util.Utility(param0,N,ecivil,children,X,psfe,year)

# I need the X vector (women's characteristic)
supply_salary = model.supply_salary()
supply_salary
#supply_salary_ret = np.log(np.random.uniform(100000,500000,(3000)))
#supply_salary_ret

# btm vector bonus
get_bonus = model.btm_score()

#Real score btm
print("Vector Bonus")
btm_score = model.btm_score()
btm = model.btm_bonus(btm_score,supply_salary)
print(btm)

#noise score btm
print("Shock btm")
btm_noise = model.btm_noise()
btm_false = model.btmfalse(btm_noise,supply_salary)
print(btm_false)

#disuti_texamp = np.zeros(N)
        
#disuti_texamp[np.logical_and(work_d == 1, btm[1] == 1)] = 1

#desut_number = delta[0]*disuti_texamp

#print(btm[0][12])

#shock_information = model.information()
#print(shock_information)

print("Income with decision")
income = model.income(work_d,supply_salary,btm_score,btm)
print(income)

print("Utility")
utilidad = model.utility(income,work_d,btm)
print(utilidad)

print("Utility simdata")
modelSD = sd.SimData(N,model)

util_all = modelSD.util(work_d,btm_d)
print(util_all[0])

print("Utility Choice")
data_sim_btm = modelSD.choice()
print(data_sim_btm["Opt Utility"])
print(data_sim_btm["Opt Work"])
print(data_sim_btm["Opt BTM"])
print(data_sim_btm["Opt Income"])

btm_opt = data_sim_btm["Opt BTM"]
work_opt = data_sim_btm["Opt Work"]



#3 opciones con btm 
#todo con self

#work_d1 = np.zeros(N)
#work_d2 = np.ones(N)
#btm_d1 = np.zeros(N)
#btm_d2 = np.ones(N)

#u_0 = modelSD.util(work_d1,btm_d1)
#u_1 = modelSD.util(work_d2,btm_d1)
#u_3 = modelSD.util(work_d2,btm_d2)
#esto es la utilidad percibida, puntaje con ruido
#u_v2 = np.array([u_0[0], u_1[0], u_3[0]]).T

#u_v3 = np.array([u_v2[:,0], u_v2[:,1]]).T

#veamos = np.argmax(u_v2, axis=1)
#veamos_v2 = np.argmax(u_v3, axis=1)

#shock_information_vvv = np.random.binomial(1,s_info,N)

#zzzz_creo = shock_information_vvv*veamos

#zzzz_creo[np.logical_and(zzzz_creo == 0, veamos_v2 == 1)] = 1

#work_opt_vjkahjkdsj = np.zeros(N)

#work_opt_vjkahjkdsj[shock_information_vvv==1] = veamos

#work_sksjdjfh = 

#work_decision = np.zeros(N)

#opt_final = np.where(((psfe_false<=98) & (self.year == 2012)) | ((psfe_false<=98) & (self.year == 2013)) | ((psfe_false<=104) & (self.year == 2014)) | 
#                     ((psfe_false<=113) & (self.year == 2015)), 1, work_decision)

#work_decision[shock_information_vvv == 1] = np.argmax(u_v2, axis=1)
#work_decision[shock_information_vvv == 0] = np.argmax(u_v3, axis=1)

#shock_information_vvv = np.random.binomial(1,s_info,N)
#Repito el experimento N veces, de tener que el 
# shock sea positivo con una probabilida de 0.5









