# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 21:27:57 2023

@author: Patricio De Araya
"""

#from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import pickle
import itertools
import sys, os
from scipy import stats
#from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from joblib import Parallel, delayed
from scipy import interpolate
import matplotlib.pyplot as plt
#sys.path.append("/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers")
#sys.path.append("D:\Git\ExpSIMCE")
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_profe_fit")
import time
import utility_btm as util
import parameters_btm as parameters
import simdata_btm as sd
import estimate_btm as est


np.random.seed(123)

#betas_nelder  = np.load("/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/betasopt_model_v22.npy")

moments_vector = np.load("C:\\Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\old\Local_teacher_julio13/moments_v2023.npy")

#data = pd.read_stata('D:\Git\ExpSIMCE/data_pythonpast.dta')

#### **** Parameters **** ####

gammas_x = [0.1,0.2,0.3]
alphas_es = [0.75, 0.25, 98, 6320]
delta = [5, 8, 3]

mar_workload = np.load('mar_work_model.npy', allow_pickle=True)
dmar_workload = np.load('dmar_work_model.npy', allow_pickle=True)
dont_workload = np.load('dont_work_model.npy', allow_pickle=True)

#sigma_foc_score = np.random.randint(0,30,(3000))
#sigma_foc_score = 15 s_info = 0.5
# Shocks = [shock btm_noise,shock info]
# Shocks = [sigma_foc_score,s_info]

shocks = [15, 0.5]

######################## **** **** ########################

#print(mar_workload[0][3])


shock_test_n = np.random.randn(3)

a = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
b = np.array([0.5, 0.5, 0.5])

c = a.dot(b)
#y = np.log(c) + np.log(shock_test_n)
educ = np.random.randint(5,13,(3000))
age = np.random.randint(25,59,(3000))
age_2 = np.power(age,2)
data_reg_btm_v1 = {'educ': educ, 'age': age, 'age2': age_2}
data_reg_btm = pd.DataFrame(data_reg_btm_v1)
X = data_reg_btm.values

#data_disc_X = data_reg_btm[(data_reg_btm['age'] >= 30) & (data_reg_btm['age'] <= 50)]


#creo variables que estén tabla, también betas en log

year = np.random.randint(2012,2016,(3000))
psfe = np.random.randint(90,120,(3000))
N = np.size(psfe)
ecivil = np.random.randint(0,2,(3000))
children = np.random.randint(0,4,(3000))
#shock_information = np.random.randint(0,2,(3000))
#work_d = np.random.randint(0,2,(3000))
#btm_d = np.random.randint(0,2,(3000))
cutoff = np.random.randint(-13,20,(3000))


#v_fs_desk = np.random.normal(0, sigma_foc_score, N)

#psfe_false_desk = psfe + v_fs_desk

#see_shock = np.random.normal(0, sigma_foc_score, N)


param0 = parameters.Parameters(gammas_x,mar_workload,dmar_workload,dont_workload,shocks,delta)
#matriz identidad
ses_opt_list = [0.0827913, 0.00373821, 0.00977805, 0.00686632]
ses_opt = np.array(ses_opt_list)

w_matrix = np.zeros((ses_opt.shape[0], ses_opt.shape[0]))
for j in range(ses_opt.shape[0]):
    w_matrix[j,j] = ses_opt[j]**(-2)

output_ins = est.estimate(cutoff,param0,N,ecivil,children,X,psfe,year,moments_vector, \
                          w_matrix)

#model = util.Utility(param0,N,ecivil,children,X,psfe,year)

#modelSD = sd.SimData(param0,N,model)

#out_boot = output_ins.simulation(50, modelSD)

#betas_list = [0.3, 0.2, 15, 0.1]
#betas = np.array(betas_list)

#obj_function = output_ins.objfunction(betas)

start_time = time.time()

output = output_ins.optimizer()

time_opt=time.time() - start_time
print ('Done in')
print("--- %s seconds ---" % (time_opt))

beta_1 = output.x[0]
beta_2 = output.x[1]
beta_3 = output.x[2]
beta_4 = output.x[3]

betas_opt_me = np.array([beta_1, beta_2,beta_3,	beta_4])



"""
print(out_boot['Por opt work'])
print(out_boot['Por opt work btm'])
print(out_boot['Por opt work W btm'])
print(out_boot['Mean income'])
print(out_boot['Por not eligible'])
print(out_boot['Por not apply'])
print(out_boot['Score equal'])

#print("Utility Choice")
#data_sim_btm = modelSD.choice()

#btm_opt = data_sim_btm["Opt BTM"]
#work_opt = data_sim_btm["Opt Work"]


work_d1mm = np.zeros(N)
work_d2mm = np.ones(N)
btm_d1mm = np.zeros(N)
btm_d2mm = np.ones(N)
#3 opciones con btm 


#todo con self
u_0mm = modelSD.util(work_d1mm,btm_d1mm)
u_1mm = modelSD.util(work_d2mm,btm_d1mm)
u_3mm = modelSD.util(work_d2mm,btm_d2mm)

#esto es la utilidad percibida, puntaje con ruido
u_v2mm = np.array([u_0mm[1], u_1mm[1], u_3mm[1]]).T
u_v3mm = np.array([u_v2mm[:,0], u_v2mm[:,1]]).T

###  Not eligible, applicants ###
moment_neamm = np.zeros(N)
btm_score_optmm = u_3mm[2]
btm_noise_optmm = u_3mm[3][0]

moment_neamm[np.logical_and(btm_score_optmm == 0, btm_noise_optmm == 1)] = 1


#option_opt = np.argmax(u_v2, axis=1)
option_opt_si1mm = np.argmax(u_v2mm, axis=1)
option_opt_si0mm = np.argmax(u_v3mm, axis=1)
"""