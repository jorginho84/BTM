#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 17:33:39 2021

@author: jorge-home

This code computes fit anaylisis

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
sys.path.append("C:\\Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13")
#sys.path.append("D:\Git\WageError")
#import gridemax
import time
#import int_linear
import utility as util
import parameters as parameters
import simdata as sd
import estimate as est
#import pybobyqa
#import xlsxwriter
from openpyxl import load_workbook


np.random.seed(123)

#betas_nelder  = np.load("D:\Git\ExpSIMCE/betasopt_model_RA3.npy")
betas_nelder  = np.load("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/betasopt_model_v25.npy")

#moments_vector = np.load("D:\Git\ExpSIMCE/moments.npy")
moments_vector = np.load("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/moments_v2023.npy")

#ajhdsajk = moments_vector[0,1]

#data = pd.read_stata('D:\Git\ExpSIMCE/data_pythonpast.dta')
#data = pd.read_stata('C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/data_pythonpast_v2023.dta')
data= pd.read_pickle("data_pythonv.pkl")

ses_opt = np.load("C:\\Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/ses_model_v2023.npy")



#count_nan = data['zpjeport'].isnull().sum()
#print('Count of nan: ' +str(count_nan))
#count_nan_1 = data['zpjeprue'].isnull().sum()
#print('Count of nan: ' +str(count_nan_1))

# TREATMENT #
treatment = np.array(data['d_trat'])

# EXPERIENCE #
years = np.array(data['experience'])

# SCORE PORTFOLIO #
p1_0 = np.array(data['score_port_past'])
p1 = np.array(data['score_port'])

# SCORE TEST #
p2_0 = np.array(data['score_test_past'])
p2 = np.array(data['score_test'])

# CATEGORY PORTFOLIO #
catPort = np.array(data['cat_port'])

# CATEGORY TEST #
catPrueba = np.array(data['cat_test'])

# TRAME #
#Recover initial placement from data (2016) 
TrameI = np.array(data['trame'])

#TrameInitial = data[['tramo_a2016']]
#TrameI = data['tramo_a2016'].to_numpy()

# TYPE SCHOOL #
typeSchool = np.array(data['typeschool'])

# Priority #
priotity = np.array(data['por_priority'])

AEP_priority = np.array(data['priority_aep'])

rural_rbd = np.array(data['rural_rbd'])

locality = np.array(data['AsignacionZona'])

#### PARAMETERS MODEL ####

N = np.size(p1_0)

HOURS = np.array([44]*N)

alphas = [[betas_nelder[0], betas_nelder[1],0,betas_nelder[2],
      betas_nelder[3], betas_nelder[4]],
     [betas_nelder[5], 0,betas_nelder[6],betas_nelder[7],
      betas_nelder[8], betas_nelder[9]]]

betas = [betas_nelder[10], betas_nelder[11], betas_nelder[12] ,betas_nelder[13],betas_nelder[14]]
gammas = [betas_nelder[15],betas_nelder[16],betas_nelder[17]]


# basic rent by hour in dollar (average mayo 2020, until 13/05/2020) *
# value hour (pesos)= 14403 *
# value hour (pesos)= 15155 *

dolar= 600

value = [14403, 15155]

hw = [value[0]/dolar,value[1]/dolar]

porc = [0.0338, 0.0333]


#inflation adjustemtn: 2012Jan-2020Jan: 1.111
Asig = [150000*1.111,100000*1.111,50000*1.111]
AEP = [Asig[0]/dolar,Asig[1]/dolar,Asig[2]/dolar]

# *** This is withouth teaching career ***
# * value professional qualification (pesos)= 72100 *
# * value professional mention (pesos)= 24034 *
# *** This is with teaching career ***
# * value professional qualification (pesos)= 253076 *
# * value professional mention (pesos)= 84360 *

#inflation adjustemtn: 2012Jan-2020Jan: 1.111***
qualiPesos = [72100*1.111, 24034*1.111, 253076, 84360] 

pro = [qualiPesos[0]/dolar, qualiPesos[1]/dolar, qualiPesos[2]/dolar, qualiPesos[3]/dolar]

#* Progression component by tranche *
#* value progression initial (pesos)= 14515
#* value progression early (pesos)= 47831
#* value progression advanced (pesos)= 96266
#* value progression advanced (pesos)= 99914 Fixed component
#* value progression expert 1 (pesos)= 360892
#* value progression expert 1 (pesos)= 138769 Fixed component
#* value progression expert 2 (pesos)= 776654
#* value progression expert 2 (pesos)= 210929 Fixed component

progress = [14515, 47831, 96266, 99914, 360892, 138769, 776654, 210929]

pol = [progress[0]/dolar, progress[1]/dolar, progress[2]/dolar, progress[3]/dolar,  
           progress[4]/dolar, progress[5]/dolar, progress[6]/dolar, progress[7]/dolar]

pri = [48542,66609,115151]
priori = [pri[0]/dolar, pri[1]/dolar, pri[2]/dolar]
    

param0 = parameters.Parameters(alphas,betas,gammas,hw,porc,pro,pol,AEP,priori)

model = util.Utility(param0,N,p1_0,p2_0,years,treatment,typeSchool,HOURS,p1,p2,catPort,catPrueba,
                     TrameI,priotity,rural_rbd,locality, AEP_priority)

modelSD = sd.SimData(N,model)


"""
opt = modelSD.choice()
simce = opt['Opt Simce']
np.var(simce[treatment == 1])
np.mean(simce[treatment == 1]) - np.mean(simce[treatment == 0])

"""

#ses_opt = np.load("D:\Git\ExpSIMCE/ses_model.npy")
ses_opt = np.load("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/ses_model_v2023.npy")
w_matrix = np.zeros((ses_opt.shape[0],ses_opt.shape[0]))


for j in range(ses_opt.shape[0]):
    w_matrix[j,j] = ses_opt[j]**(-2)
    

output_ins = est.estimate(N, years,param0, p1_0,p2_0,treatment, \
                 typeSchool,HOURS,p1,p2,catPort,catPrueba,TrameI,priotity,rural_rbd,locality, AEP_priority, \
                 w_matrix,moments_vector)
    
#bienniumtwoFalse = years/2
#biennium = np.floor(bienniumtwoFalse)
#biennium[biennium>15]=15

       
       
corr_data = output_ins.simulation(50,modelSD)
#print(corr_data)

beta0 = np.array([param0.alphas[0][0],
                          param0.alphas[0][1],
                          param0.alphas[0][3],  
                          np.log(param0.alphas[0][4]),
                          param0.alphas[0][5],
                          param0.alphas[1][0],
                          param0.alphas[1][2],
                          param0.alphas[1][3],
                          np.log(param0.alphas[1][4]),
                          param0.alphas[1][5],
                          param0.betas[0],
                          param0.betas[1],
                          param0.betas[2],
                          param0.betas[3],
                          param0.betas[4],
                          param0.gammas[0],
                          param0.gammas[1],
                          param0.gammas[2]])

qw = output_ins.objfunction(beta0)

##### PYTHON TO EXCEL #####

#wb = load_workbook('D:\Git\ExpSIMCE/Outcomes.xlsx')
wb = load_workbook('C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/Outcomes_v2023_vp.xlsx')
sheet = wb["data"]

sheet['C5'] = 'Mean Portfolio'
sheet['C6'] = 'Variance Portfolio'
sheet['C7'] = 'Mean SIMCE'
sheet['C8'] = 'Variance SIMCE'
sheet['C9'] = 'Mean Test'
sheet['C10'] = 'Variance Test'
sheet['C11'] = 'Mean Portfolio-Test'
sheet['C12'] = '\% Intermediate'
sheet['C13'] = '\% Advanced'
sheet['C14'] = '\% Expert'
sheet['C15'] = 'corr(Port,Simce)'
sheet['C16'] = 'corr(Test,Simce)'
sheet['C17'] = 'corr(exp,Port)'
sheet['C18'] = 'corr(exp,Test)'
sheet['C19'] = '\% adva/expert control'
sheet['C20'] = 'Corr(Port,p)'
sheet['C21'] = 'Corr(Test,p)'
sheet['C22'] = 'Corr(Simce,Exp)'
sheet['D4'] = 'simulation'
sheet['E4'] = 'data'
sheet['F4'] = 'se'

sheet['D5'] = corr_data['Mean Portfolio']
sheet['D6'] = corr_data['Var Port']
sheet['D7'] = corr_data['Mean SIMCE']
sheet['D8'] = corr_data['Var SIMCE']
sheet['D9'] = corr_data['Mean Test']
sheet['D10'] = corr_data['Var Test']
sheet['D11'] = corr_data['Mean PortTest']
sheet['D12'] = corr_data['perc inter']
sheet['D13'] = corr_data['perc advanced']
sheet['D14'] = corr_data['perc expert']
sheet['D15'] = corr_data['Estimation SIMCE vs Portfolio']
sheet['D16'] = corr_data['Estimation SIMCE vs Prueba']
sheet['D17'] = corr_data['Estimation EXP vs Portfolio']
sheet['D18'] = corr_data['Estimation EXP vs Prueba']
sheet['D19'] = corr_data['perc adv/exp control']
sheet['D20'] = corr_data['Estimation Test vs p']
sheet['D21'] = corr_data['Estimation Portfolio vs p']
sheet['D22'] = corr_data['Estimation SIMCE vs Experience']




sim = np.array([corr_data['Mean Portfolio'],
corr_data['Var Port'],
corr_data['Mean SIMCE'],
corr_data['Var SIMCE'],
corr_data['Mean Test'],
corr_data['Var Test'],
corr_data['Mean PortTest'],
corr_data['perc inter'],
corr_data['perc advanced'],
corr_data['perc expert'],
corr_data['Estimation SIMCE vs Portfolio'],
corr_data['Estimation SIMCE vs Prueba'],
corr_data['Estimation EXP vs Portfolio'],
corr_data['Estimation EXP vs Prueba'],
corr_data['Estimation SIMCE vs Experience'],
corr_data['perc adv/exp control'],
corr_data['Estimation Test vs p'],
corr_data['Estimation Portfolio vs p']])

x_vector = sim - moments_vector

q_w = np.dot(np.dot(np.transpose(x_vector),w_matrix),x_vector)

#weight = x_vector**2/ses_opt**2


#wb.save('D:\Git\ExpSIMCE/Outcomes.xlsx')
wb.save('C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/Outcomes_v2023_vp.xlsx')


with open('C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_julio13/fit_table.tex','w') as f:
    f.write(r'\footnotesize{'+'\n')
    f.write(r'\begin{tabular}{llccccc}'+'\n')
    f.write(r'\toprule'+'\n')
    f.write(r'& Moment &  & Model &  & Data  &  & S.E. data \\'+'\n')
    f.write(r'\midrule'+'\n')
    f.write(r'A. Treatment group  (2016 teachers) &  &       &  &       &  & \\'+'\n')
    f.write(r'Mean Portfolio                      &  & '+'{:1.2f}'.format(sim[0]) +r' &  & '+'{:1.2f}'.format(moments_vector[0]) +r'   &  & '+'{:1.3f}'.format(ses_opt[0]) +r' \\'+'\n')
    f.write(r'Variance Portfolio                  &  & '+'{:1.2f}'.format(sim[1]) +r' &  & '+'{:1.2f}'.format(moments_vector[1]) +r'   &  & '+'{:1.3f}'.format(ses_opt[1]) +r' \\'+'\n')
    f.write(r'Mean PKT                            &  & '+'{:1.2f}'.format(sim[4]) +r' &  & '+'{:1.2f}'.format(moments_vector[4]) +r'   &  & '+'{:1.3f}'.format(ses_opt[4]) +r' \\'+'\n')
    f.write(r'Variance PKT                        &  & '+'{:1.2f}'.format(sim[5]) +r' &  & '+'{:1.2f}'.format(moments_vector[5]) +r'   &  & '+'{:1.3f}'.format(ses_opt[5]) +r' \\'+'\n')
    f.write(r'\% Intermediate                     &  & '+'{:1.2f}'.format(sim[7]*100) +r' &  & '+'{:1.2f}'.format(moments_vector[7]*100) +r'   &  & '+'{:1.3f}'.format(ses_opt[7]) +r' \\'+'\n')
    f.write(r'\% Advanced                         &  & '+'{:1.2f}'.format(sim[8]*100) +r' &  & '+'{:1.2f}'.format(moments_vector[8]*100) +r'   &  & '+'{:1.3f}'.format(ses_opt[8]) +r' \\'+'\n')
    f.write(r'\% Expert                           &  & '+'{:1.2f}'.format(sim[9]*100) +r' &  & '+'{:1.2f}'.format(moments_vector[9]*100) +r'   &  & '+'{:1.3f}'.format(ses_opt[9]) +r' \\'+'\n')
    f.write(r'corr(Port,Simce)                    &  & '+'{:1.2f}'.format(sim[10]) +r' &  & '+'{:1.2f}'.format(moments_vector[10]) +r'   &  & '+'{:1.3f}'.format(ses_opt[10]) +r' \\'+'\n')
    f.write(r'corr(Test,Simce)                    &  & '+'{:1.2f}'.format(sim[11]) +r' &  & '+'{:1.2f}'.format(moments_vector[11]) +r'   &  & '+'{:1.3f}'.format(ses_opt[11]) +r' \\'+'\n')
    f.write(r'corr(exp,Port)                      &  & '+'{:1.2f}'.format(sim[12]) +r' &  & '+'{:1.2f}'.format(moments_vector[12]) +r'   &  & '+'{:1.3f}'.format(ses_opt[12]) +r' \\'+'\n')
    f.write(r'corr(exp,Test)                      &  & '+'{:1.2f}'.format(sim[13]) +r' &  & '+'{:1.2f}'.format(moments_vector[13]) +r'   &  & '+'{:1.3f}'.format(ses_opt[13]) +r' \\'+'\n')
    f.write(r'Corr(Port,p)                        &  & '+'{:1.2f}'.format(sim[17]) +r' &  & '+'{:1.2f}'.format(moments_vector[17]) +r'   &  & '+'{:1.3f}'.format(ses_opt[17]) +r' \\'+'\n')
    f.write(r'Corr(Test,p)                        &  & '+'{:1.2f}'.format(sim[16]) +r' &  & '+'{:1.2f}'.format(moments_vector[16]) +r'   &  & '+'{:1.3f}'.format(ses_opt[16]) +r' \\'+'\n')
    f.write(r'                                    &  &       &  &       &  &       \\'+'\n')
    f.write(r'B. Control group (2018- teachers)   &  &       &  &       &  &       \\'+'\n')
    f.write(r'Average of past portfolio-test      &  & '+'{:1.2f}'.format(sim[6]) +r' &  & '+'{:1.2f}'.format(moments_vector[6]) +r'   &  & '+'{:1.3f}'.format(ses_opt[6]) +r' \\'+'\n')
    f.write(r'\% advanced or expert               &  & '+'{:1.2f}'.format(sim[15]*100) +r' &  & '+'{:1.2f}'.format(moments_vector[15]*100) +r'   &  & '+'{:1.3f}'.format(ses_opt[15]) +r' \\'+'\n')
    f.write(r'                                    &  &       &  &       &  &       \\'+'\n')
    f.write(r'C. Full sample                      &  &       &  &       &  &       \\'+'\n')
    f.write(r'Mean SIMCE                          &  & '+'{:1.2f}'.format(sim[2]) +r' &  & '+'{:1.2f}'.format(moments_vector[2]) +r'   &  & '+'{:1.3f}'.format(ses_opt[2]) +r' \\'+'\n')
    f.write(r'Variance SIMCE                      &  & '+'{:1.2f}'.format(sim[3]) +r' &  & '+'{:1.2f}'.format(moments_vector[3]) +r'   &  & '+'{:1.3f}'.format(ses_opt[3]) +r' \\'+'\n')
    f.write(r'Corr(Simce,Exp)                     &  & '+'{:1.2f}'.format(sim[14]) +r' &  & '+'{:1.2f}'.format(moments_vector[14]) +r'   &  & '+'{:1.3f}'.format(ses_opt[14]) +r' \\'+'\n')
    f.write(r'\bottomrule'+'\n')
    f.write(r'\end{tabular}'+'\n')
    f.write(r'}'+'\n')
    f.close()


"""
opt = modelSD.choice()
print('OPt effort % no effort, control', np.mean(opt['Opt Effort'][treatment == 0] == 0))
print('OPt effort % no effort, treatment', np.mean(opt['Opt Effort'][treatment == 1] == 0))

print('Mean income, control', np.mean(opt['Opt Income'][1][treatment == 0]))
print('Mean income, treatment', np.mean(opt['Opt Income'][0][treatment == 1]))
"""