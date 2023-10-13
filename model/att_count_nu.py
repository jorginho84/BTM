"""
This script computes the ATT of BTM across informational sets (noise levels)

"""

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
#sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_profe_fit")
import time
import utility_btm as util
import parameters_btm as parameters
import simdata_btm as sd
import estimate_btm as est
import statsmodels.api as sm


np.random.seed(123)


#betas_hat  = np.load("/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/betasopt_model_v22.npy")


############ **** Parameters **** ################
delta = [betas_hat[0], betas_hat[1]]
shocks = [betas_hat[2], betas_hat[3]]
gammas_x = [betas_hat[4],betas_hat[5],betas_hat[6],betas_hat[7],betas_hat[8]]

mar_workload = np.load('mar_work_model.npy', allow_pickle=True)
dmar_workload = np.load('dmar_work_model.npy', allow_pickle=True)
dont_workload = np.load('dont_work_model.npy', allow_pickle=True)




############ **** External data **** ############
year = np.random.randint(2012,2016,(3000))
psfe = np.random.randint(90,120,(3000))
N = np.size(psfe)
ecivil = np.random.randint(0,2,(3000))
children = np.random.randint(0,4,(3000))
educ = np.random.randint(5,13,(3000))
age = np.random.randint(25,59,(3000))
age_2 = np.power(age,2)
data_reg_btm_v1 = {'educ': educ, 'age': age, 'age2': age_2}
data_reg_btm = pd.DataFrame(data_reg_btm_v1)
X = data_reg_btm.values


############ **** Counterfactual choices **** ############

#Counterfactual choices
n_sim = 50
nu_levels = [betas_hat[2]*0.8, betas_hat[2]*0.5, betas_hat[2]*0.3, betas_hat[2]*0.01]
params = []
models = []
modelsSD = []
work = np.zeros((N,n_sim,len(nu_levels)))


#Counterfactual: no access to BTM (k=0)
params.append(parameters.Parameters(gammas_x,married,married,dont_workload,[betas_hat[2], 0],delta))
models.append(util.Utility(params[0], N, ecivil, children, X, psfe, year,educ,age,age_2))
modelsSD.append(sd.SimData(params[0], N, models[0]))

#Treatments: access to BTM (with prob of knowing fixed), yet with less noise.
for j in range(len(nu_levels)):
	params.append(parameters.Parameters(gammas_x,married,married,dont_workload,[nu_levels[j], betas_hat[3]],delta))
	models.append(util.Utility(params[j+1], N, ecivil, children, X, psfe, year,educ,age,age_2))
	modelsSD.append(sd.SimData(params[j+1], N, models[j+1]))

#Simulating choices for each model
for j in range(len(nu_levels) + 1):
	for i in range(n_sim):
			opt = modelSD[j].choice()
			work[:,i,j] = opt_control['Opt Work']

#Prob of working in each simulation
work = np.mean(work_sim, axis = 1)

#Changes in individual probabilities (individual-level TE)
ate_work = np.zeros((N,len(nu_levels)))
for j in range(len(nu_levels)):
	ate_work[:,j] = work[:,j+1] - work[:,0]

############ **** FIGURE: ATE across PFSE (original) and K levels **** ############

#Categories of PFSE
cat_pfse = np.arange(0,-100,-15)
att = np.zeros(cat_pfse.size - 1)

#ATTs across PFSE
att = np.zeros((cat_pfse.size - 1,len(nu_levels)))
for k in range(len(nu_levels)):
	for j in range(cat_pfse.size - 1):
		att[j,k] = np.mean(ate_work[(pfse <= cat_pfse[j]) & (psfe > cat_pfse[j+1]),k])

#Figure
x_points = np.zeros()
for j in range(cat_pfse.size - 1):
	x_points[j] =  (abs(cat_pfse[j+1]) - abs(cat_pfse[j]))/2

colors_list = ['navy', 'lightskyblue' , 'sandybrown', 'darkorange' ]

label_list = []
for j in range(len(nu_levels)):
	label_list.append(r'$\simga^2_\nu$ = ' + '{:04.2f}'.format(nu_levels[j+1]))

fig, ax = plt.subplots()
for j in range(len(nu_levels)):
	ax.plot(x_points,att,'--o',colorv = colors_list[j] ,alpha = .8, label = label_list[j])
ax.set_ylabel(r'Effect on employment', fontsize=13)
ax.set_xlabel(r'Vulnerability score', fontsize=13)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
ax.set_xticks(x_points)
ax.set_xticklabels(['(-15,0]','(-30,-15]','(-45,-30]','(-60,-45]','(-75,-60]','(-90,75]'])
#ax.set_ylim(0,0.3)
ax.legend(loc = 'bottom right',fontsize = 13)
plt.tight_layout()
plt.show()
#fig.savefig('/Users/jorge-home/Dropbox/Research/teachers-reform/teachers/Results/counterfactual_percentiles.pdf', format='pdf')


