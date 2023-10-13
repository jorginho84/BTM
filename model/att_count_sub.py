"""
This script computes the ATT of BTM across different bonus sizes

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




