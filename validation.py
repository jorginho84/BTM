"""
This script computes a validation analysis.

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

param0 = parameters.Parameters(gammas_x,married,married,dont_workload,shocks,delta)


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

############ **** Baseline choices **** ############
param0 = parameters.Parameters(gammas_x,mar_workload,dmar_workload,dont_workload,shocks,delta)
model = util.Utility(param0, N, ecivil, children, X, psfe, year,educ,age,age_2)

work_sim = np.zeros((N,n_sim))
btm_takeup_sim = np.zeros((N,n_sim))

n_sim = 50
for i in range(1,n_sim):
	opt = modelSD.choice()
	work[:,i] = opt['Opt Work']
	btm_takeup[:,i] = opt['Opt BTM']

work = np.mean(work_sim, axis = 1)
btm_takeup = np.mean(btm_takeup_sim, axis = 1)

############ **** Figure 1: take-up across PFSE **** ############

df = pd.DataFrame({'psfe': psfe[(psfe <= 15) & (psfe >= -15)], 'btm': btm_takeup[(psfe <= 15) & (psfe >= -15)]})
linear_model_left = sm.OLS(df['btm'],sm.add_constant(df['psfe'][psfe <= 0])).fit()
x_points_left = np.arange(-15,0.5,0)
predictions_left = linear_model.get_prediction(sm.add_constant(x_points_left))
intervals_left = predictions.conf_int(alpha = 0.05)

means_y_left = np.zeros(x_points_left.size[0]-1)
for j in range(x_points_left.size[0]-1):
	means_y_left = np.mean(btm_takeup[(psfe >= x_points_left[j]) & (psfe < x_points_left[j+1])])

linear_model_right = sm.OLS(df['btm'],sm.add_constant(df['psfe'][psfe > 0])).fit()
x_points_right = np.arange(0,0.5,15)
predictions_right = linear_model.get_prediction(sm.add_constant(x_points_right))
intervals_right = predictions.conf_int(alpha = 0.05)

means_y_right = np.zeros(x_points_right.size[0]-1)
for j in range(x_points_right.size[0]-1):
	means_y_right = np.mean(btm_takeup[(psfe >= x_points_right[j]) & (psfe < x_points_right[j+1])])

fig, ax=plt.subplots()
plot1 = ax.plot(x_points_left,predictions_left,'-',alpha = .8, color='blue')
plot2 = ax.plot(x_points_left,means_y_left,'o' ,alpha=.5, color = 'blue')
plot3 = ax.fill_between(x_points_left, intervals_left[:, 0], intervals_left[:, 1], color='gray', alpha=0.3)

plot4 = ax.plot(x_points_right,predictions_right,'-',alpha = .8, color='blue')
plot5 = ax.plot(x_points_right,means_y_right,'o' ,alpha=.5, color = 'blue')
plot6 = ax.fill_between(x_points_right, intervals_right[:, 0], intervals_right[:, 1], color='gray', alpha=0.3)

ax.set_ylabel(r'Vulnerability score', fontsize=13)
ax.set_xlabel(r'Simulated take-up', fontsize=13)
#ax.set_xticks([1,2,3,4,5])
#ax.set_xticklabels([ r'$\leq$ 10', '11-17','18-27', '28-35', r'36$\leq$'])
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
#ax.set_ylim(0,0.12)
ax.get_legend().remove()
plt.tight_layout()
plt.show()
#fig.savefig('/Users/jorge-home/Dropbox/Research/teachers-reform/teachers/Results/counterfactual_exp_lines.pdf', format='pdf')

############ **** Figure 2: RDD employment effects **** ############
df = pd.DataFrame({'psfe': psfe[(psfe <= 15) & (psfe >= -15)], 'work': work[(psfe <= 15) & (psfe >= -15)]})

linear_model_left = sm.OLS(df['work'],sm.add_constant(df['psfe'][psfe <= 0])).fit()
x_points_left = np.arange(-15,0.5,0)
predictions_left = linear_model.get_prediction(sm.add_constant(x_points_left))
intervals_left = predictions.conf_int(alpha = 0.05)

means_y_left = np.zeros(x_points_left.size[0]-1)
for j in range(x_points_left.size[0]-1):
	means_y_left = np.mean(work[(psfe >= x_points_left[j]) & (psfe < x_points_left[j+1])])

linear_model_right = sm.OLS(df['work'],sm.add_constant(df['psfe'][psfe > 0])).fit()
x_points_right = np.arange(0,0.5,15)
predictions_right = linear_model.get_prediction(sm.add_constant(x_points_right))
intervals_right = predictions.conf_int(alpha = 0.05)

means_y_right = np.zeros(x_points_right.size[0]-1)
for j in range(x_points_right.size[0]-1):
	means_y_right = np.mean(work[(psfe >= x_points_right[j]) & (psfe < x_points_right[j+1])])

fig, ax=plt.subplots()
plot1 = ax.plot(x_points_left,predictions_left,'-',alpha = .8, color='blue')
plot2 = ax.plot(x_points_left,means_y_left,'o' ,alpha=.5, color = 'blue')
plot3 = ax.fill_between(x_points_left, intervals_left[:, 0], intervals_left[:, 1], color='gray', alpha=0.3)

plot4 = ax.plot(x_points_right,predictions_right,'-',alpha = .8, color='blue')
plot5 = ax.plot(x_points_right,means_y_right,'o' ,alpha=.5, color = 'blue')
plot6 = ax.fill_between(x_points_right, intervals_right[:, 0], intervals_right[:, 1], color='gray', alpha=0.3)

ax.set_ylabel(r'Vulnerability score', fontsize=13)
ax.set_xlabel(r'Simulated work probability', fontsize=13)
#ax.set_xticks([1,2,3,4,5])
#ax.set_xticklabels([ r'$\leq$ 10', '11-17','18-27', '28-35', r'36$\leq$'])
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
#ax.set_ylim(0,0.12)
ax.get_legend().remove()
plt.tight_layout()
plt.show()
#fig.savefig('/Users/jorge-home/Dropbox/Research/teachers-reform/teachers/Results/counterfactual_exp_lines.pdf', format='pdf')


