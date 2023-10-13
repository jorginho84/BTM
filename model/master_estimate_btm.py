# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 21:27:57 2023

@author: Patricio De Araya
"""

#from __future__ import division #omit for python 3.x
from __future__ import division
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
import statsmodels.api as sm


np.random.seed(123)

#betas_nelder  = np.load("/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/betasopt_model_v22.npy")
moments_vector_list = [4, 7, 10.5, 0.35, 11, 9, 45, 400, 12]
moments_vector = np.array(moments_vector_list)


#data = pd.read_stata('D:\Git\ExpSIMCE/data_pythonpast.dta')

#### **** Parameters **** ####

gammas_x = [1,0.2,0.05,0.1,0.1]

#alphas_es = [0.75, 0.25, 98, 6320]
delta = [0.1, 0.1]

mar_workload = np.load('mar_work_model.npy', allow_pickle=True)
dmar_workload = np.load('dmar_work_model.npy', allow_pickle=True)
dont_workload = np.load('dont_work_model.npy', allow_pickle=True)

#sigma_foc_score = np.random.randint(0,30,(3000))
#sigma_foc_score = 15 s_info = 0.5
# Shocks = [shock btm_noise,shock info]
# Shocks = [sigma_foc_score,s_info]

shocks = [10, 0.3]
#shock_information_ngmh = np.random.binomial(1,0.5,3000)
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
cutoff = np.random.randint(-20,20,(3000))

#v_fs_desk = np.random.normal(0, sigma_foc_score, N)

#psfe_false_desk = psfe + v_fs_desk

#see_shock = np.random.normal(0, sigma_foc_score, N)

param0 = parameters.Parameters(gammas_x,mar_workload,dmar_workload,dont_workload,shocks,delta)

#matriz identidad
ses_opt_list = [0.0827913, 0.00373821, 0.00977805, 0.00686632, 0.009846, \
                0.0076253, 0.0012345, 0.0076243, 0.007653]
ses_opt = np.array(ses_opt_list)

w_matrix = np.zeros((ses_opt.shape[0], ses_opt.shape[0]))
for j in range(ses_opt.shape[0]):
    w_matrix[j,j] = ses_opt[j]**(-2)

output_ins = est.estimate(cutoff,educ,age,age_2,param0,N,ecivil,children,X,psfe,year,moments_vector, \
                          w_matrix)

"""
model = util.Utility(param0,N,ecivil,children,X,psfe,year,educ,age,age_2)


supply_salary = model.supply_salary()
supply_salary
salario_nivel = np.exp(supply_salary)
salario_nivel
#supply_salary_ret = np.log(np.random.uniform(100000,500000,(3000)))
#supply_salary_ret

# btm vector bonus
get_bonus = model.btm_score()
get_bonus
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

work_d = np.random.randint(0,2,(3000))
btm_d = np.random.randint(0,2,(3000))
income_btm = model.income(work_d,supply_salary,get_bonus,btm)

util_dddd = model.utility(income_btm, work_d, btm_d, btm_score)

shock_info = shocks[1]
shock_information = np.random.binomial(1,shock_info,N)

qwe = delta[1]*btm_d*btm_score


modelSD = sd.SimData(param0,N,model)
#opt_sd = modelSD.choice()

work_d1 = np.zeros(N)
work_d2 = np.ones(N)
btm_d1 = np.zeros(N)
btm_d2 = np.ones(N)
 #3 opciones con btm 
 
 
 #todo con self
u_0 = modelSD.util(work_d1,btm_d1)
u_1 = modelSD.util(work_d2,btm_d1)
u_3 = modelSD.util(work_d2,btm_d2)
 
 #esto es la utilidad percibida, puntaje con ruido
u_v2 = np.array([u_0[1], u_1[1], u_3[1]]).T
u_v3 = np.array([u_v2[:,0], u_v2[:,1]]).T
 
 #option_opt = np.argmax(u_v2, axis=1)
option_opt_si1 = np.argmax(u_v2, axis=1)
option_opt_si0 = np.argmax(u_v3, axis=1)
 
shock_info = shocks[1]
shock_information = np.random.binomial(1,shock_info,N)

option_opt_all = shock_information*option_opt_si1

#btm_score[work_d==0] = 0
#btm[btm_score==0] = 0

#res = np.zeros_like(btm)

#idx = btm > 0

#np.log(btm, out=res, where=idx)


#modelSD = sd.SimData(param0,N,model)
#opt_sd = modelSD.choice()


#work_d = np.random.randint(0,2,(3000))
#btm_d = np.random.randint(0,2,(3000))
#util_all = modelSD.util(work_d,btm_d)
#print(util_all[0])

#betas_list = [0.3, 0.2, 15, 0.1]
#betas = np.array(betas_list)

#obj_function = output_ins.objfunction(betas)

#out_boot = output_ins.simulation(50, modelSD)
"""

start_time = time.time()

output = output_ins.optimizer()

time_opt=time.time() - start_time
print ('Done in')
print("--- %s seconds ---" % (time_opt))

beta_1 = output.x[0]
beta_2 = output.x[1]
beta_3 = output.x[2]
beta_4 = output.x[3]
beta_5 = output.x[4]
beta_6 = output.x[5]
beta_7 = output.x[6]
beta_8 = output.x[7]
beta_9 = output.x[8]

betas_opt_me = np.array([beta_1, beta_2,beta_3,	beta_4, \
                         beta_5, beta_6, beta_7, beta_8, beta_8])
betas_opt_me



#print(out_boot['Por opt work'])
#print(out_boot['Por opt work btm'])
#print(out_boot['Por opt work W btm'])
#print(out_boot['Mean income'])
#print(out_boot['Por not eligible'])
#print(out_boot['Por not apply'])


#print("Utility Choice")
#data_sim_btm = modelSD.choice()

#btm_opt = data_sim_btm["Opt BTM"]
#work_opt = data_sim_btm["Opt Work"]


"""
df = {'OPTWORK': opt_sd['Opt Work'], 'OPTBTM': opt_sd['Opt BTM'], 'OPTINCOME': opt_sd['Opt Income'],
      'ELIG_NOT': opt_sd['NEA MOMENT'], 'APPLY_NOT': opt_sd['ENA MOMENT'], 'DISCONTINUITY': cutoff, 
      'EDUCATION': educ, 'AGE': age, 'AGE_2': age_2}

data_reg = pd.DataFrame(df,columns = ['OPTWORK','OPTINCOME', 'EDUCATION', 'AGE', 'AGE_2'])

data_reg[data_reg['OPTWORK'] == 1]

y = data_reg['OPTINCOME']
x = data_reg[['EDUCATION', 'AGE', 'AGE_2']]
x = sm.add_constant(x)

model_reg = sm.OLS(endog = y, exog = x)
results = model_reg.fit()

print(results.summary())
print(results.bse)

const_res = results.params.const.round(8)
print(const_res)
educ_res = results.params.EDUCATION.round(8)
print(educ_res)
age_res = results.params.AGE.round(8)
print(age_res)
age2_res = results.params.AGE_2.round(8)
print(age2_res)
error_res = results.mse_resid.round(8)
print(error_res)
error_res = results.scale
print(error_res2)

error_resv2 = results.mse_resid**2
print(error_resv2)

std_err = np.sqrt(np.sum(results.resid_pearson ** 2) / (len(y) - len(x.columns)))
print(f'Standard Error of the Regression: {std_err:.2f}')
"""

