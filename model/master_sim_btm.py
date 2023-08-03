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
#import simdata as sd
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

gammas_x = [0.1,0.2,0.3]
alphas_es = [0.75, 0.25, 98, 6320]
delta = [5, 8, 3, 7]

mar_workload = np.load('mar_work_model.npy', allow_pickle=True)
dmar_workload = np.load('dmar_work_model.npy', allow_pickle=True)
dont_workload = np.load('dont_work_model.npy', allow_pickle=True)

s_info = 0.5

######################## **** **** ########################

print(mar_workload[0][3])


shock_test_n = np.random.randn(3)

a = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
b = np.array([0.5, 0.5, 0.5])

c = a.dot(b)

#y = np.log(c) + np.log(shock_test_n)



#creo variables que estén tabla, también betas en log

year = np.random.randint(2012,2016,(3000))
psfe = np.random.randint(90,120,(3000))
supply_salary = np.log(np.random.uniform(100000,500000,(3000)))
N = np.size(psfe)
ecivil = np.random.randint(0,2,(3000))
children = np.random.randint(0,4,(3000))
#shock_information = np.random.randint(0,2,(3000))
work_d = np.random.randint(0,2,(3000))


param0 = parameters.Parameters(gammas_x,mar_workload,dmar_workload,dont_workload,s_info,delta)
model = util.Utility(param0,N,ecivil,children)

# I need the X vector (women's characteristic)
#supply_salary = model.supply_salary()

print("Vector Bonus")
btm = model.btm(psfe,year,supply_salary)
print(btm)

#disuti_texamp = np.zeros(N)
        
#disuti_texamp[np.logical_and(work_d == 1, btm[1] == 1)] = 1

#desut_number = delta[0]*disuti_texamp

#print(btm[0][12])

shock_information = model.information()
print(shock_information)

print("Income with decision")
income = model.income(work_d,supply_salary,btm,shock_information)
print(income)

print("Utility")
utilidad = model.util(income,work_d,btm)
print(income)



