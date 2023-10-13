# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 18:14:43 2020

@author: pjac2
"""
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 16:49:00 2020

@author: pjac2
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
import seaborn as sn
from statsmodels.iolib.summary2 import summary_col
import statsmodels.api as sm
from tabulate import tabulate
from texttable import Texttable
#import xlsxwriter
from openpyxl import Workbook 
from openpyxl import load_workbook


#### LOAD DATA ####

#Data complete
#data_pythonpast = pd.read_stata('C://Users\Patricio De Araya\Dropbox\LocalRA')

### simulated data
employment = np.random.randint(0,2,(3000))
earnings = np.random.randint(45000,250000,(3000))
psfe = np.random.randint(80,110,(3000))
nea = np.zeros(psfe.size)
nea[psfe>98]=1
#mayor a cero
#nea[rev['PSFE']>98]=1
#cutoff = np.random.randint(-20,20,(3000))
ud_2012 = np.zeros(3000)
ud_2012 = psfe - 98
educ = np.random.randint(5,13,(3000))
age = np.random.randint(25,59,(3000))
age_2 = np.power(age,2)
#data_reg_btm_v1 = {'educ': educ, 'age': age, 'age2': age_2}
#data_reg_btm = pd.DataFrame(data_reg_btm_v1)
#X = data_reg_btm.values
take_up = np.random.randint(0,2,(3000))
year = np.random.randint(2012,2016,(3000))
N = np.size(psfe)
ecivil = np.random.randint(0,2,(3000))
children = np.random.randint(0,4,(3000))

data = {'WORK': employment, 'EARNINGS': earnings, 'PSFE': psfe, 'EDUC' : educ, 'AGE': age,
              'AGE_2': age_2, 'NEA': nea, 'UpDown': ud_2012, 'takeup': take_up}

data_btm = pd.DataFrame(data, columns=['WORK','EARNINGS','PSFE','EDUC','AGE','AGE_2','NEA', 'UpDown', 
                                       'takeup'])
#agregar take up
n = data_btm.shape[0]
rev = data_btm.sample(n, replace=True)
#ENA
data_ena = rev[(rev['WORK'] == 1) & (rev['UpDown'] <= 0)]

data_ud = rev[(rev['UpDown'] >= -15) & (rev['UpDown'] <= 15)]
data_ud = data_ud[data_ud['WORK']== 1]
#condicionar work, sacar promedio take up


#### BOOTSTRAP ####

def corr_simulate(data, B):
    
    n = data.shape[0]
    
    dmean_work = np.zeros(B)
    #dmean_nea = np.zeros(B)
    dmean_ena = np.zeros(B)
    dmean_ud = np.zeros(B)
    const_reg = np.zeros(B)
    educ_reg = np.zeros(B)
    age_reg = np.zeros(B)
    age2_reg = np.zeros(B)
    error_reg = np.zeros(B)
    

    
    for i in range(1,B):
        rev = data.sample(n, replace=True)
        #takeup
        dmean_work[i] = np.mean(rev['WORK'])
        #1- take_up condicionar en trabajar y condicional en estar a 
        # la izquierda del corte la gente que es elegible pero no aplica
        
        # borrar dmean_nea[i] = np.mean(rev['NEA'])
        
        # ENA: Elegible NOT applicants
        data_ena = rev[(rev['WORK'] == 1) & (rev['UpDown'] <= 0)]
        dmean_ena[i] = np.mean(data_ena['takeup']) 
        
        data_ud = rev[(rev['UpDown'] >= -15) & (rev['UpDown'] <= 15)]
        data_ud = data_ud[data_ud['WORK'] == 1]
        #condicionar work, sacar promedio take up
        dmean_ud[i] = np.mean(data_ud['takeup'])
            
        data_reg = pd.DataFrame(rev,columns = ['WORK','EARNINGS', 'EDUC', 'AGE', 'AGE_2'])
        data_reg[data_reg['WORK'] == 1]
        #log natural de earnings
        y_notlog = data_reg['EARNINGS']
        y = np.log(y_notlog)
        x = data_reg[['EDUC', 'AGE', 'AGE_2']]
        x = sm.add_constant(x)

        model_reg = sm.OLS(endog = y, exog = x)
        results = model_reg.fit()

        const_reg[i] = results.params.const.round(8)
        educ_reg[i] = results.params.EDUC.round(8)
        age_reg[i] = results.params.AGE.round(8)
        age2_reg[i] = results.params.AGE_2.round(8)
        error_reg[i] = np.sqrt(results.scale)
        
        
        
    out_data_work = np.mean(dmean_work)
    #out_data_nea = np.mean(dmean_nea)
    out_data_ena = np.mean(dmean_ena)
    out_data_ud = np.mean(dmean_ud)
    out_const_reg = np.mean(const_reg)
    out_educ_reg = np.mean(educ_reg)
    out_age_reg = np.mean(age_reg)
    out_age2_reg = np.mean(age2_reg)
    out_error_reg = np.mean(error_reg)

    
    out_dataE_work = np.std(dmean_work)
    #out_dataE_nea = np.std(dmean_nea)
    out_dataE_ena = np.std(dmean_ena)
    out_dataE_ud = np.std(dmean_ud)
    out_dataE_const_reg = np.std(const_reg)
    out_dataE_educ_reg = np.std(educ_reg)
    out_dataE_age_reg = np.std(age_reg)
    out_dataE_age2_reg = np.std(age2_reg)
    out_dataE_error_reg = np.std(error_reg)
    
    
    #var-cov matrix
    samples = np.array([dmean_work,dmean_ena,dmean_ud,const_reg,educ_reg,
                        age_reg,age2_reg,error_reg])
    
    varcov = np.cov(samples)

    return {'Work data mean': out_data_work,
            'ENA data mean': out_data_ena,
            'Takeup data mean': out_data_ud,
            'Const reg': out_const_reg,
            'Educ reg': out_educ_reg,
            'Age reg': out_age_reg,
            'Age_2 reg': out_age2_reg,
            'Error reg': out_error_reg,
            'Work data error': out_dataE_work,
            'ENA data error': out_dataE_ena,
            'Takeup data error': out_dataE_ud,
            'Const reg data error': out_dataE_const_reg,
            'Educ reg data error': out_dataE_educ_reg,
            'Age reg data error': out_dataE_age_reg,
            'Age_2 reg data error': out_dataE_age2_reg,
            'Error reg data error': out_dataE_error_reg,
            'Var Cov Matrix': varcov}


result = corr_simulate(data_btm,1000)
print(result)

varcov = result['Var Cov Matrix']
        
ses = np.array([result['Work data error'],
result['ENA data error'],
result['Takeup data error'],
result['Const reg data error'],
result['Educ reg data error'],
result['Age reg data error'],
result['Age_2 reg data error'],
result['Error reg data error']])

means = np.array([result['Work data mean'],
result['ENA data mean'],
result['Takeup data mean'],
result['Const reg'],
result['Educ reg'],
result['Age reg'],
result['Age_2 reg'],
result['Error reg']])


#np.save('/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/estimates/ses_model_v2023.npy',ses)
np.save(r'C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1\estimates\ses_model_btm.npy',ses)

#np.save('/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/estimates/moments_v2023.npy',means)
np.save(r'C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1\estimates\moments_btm.npy',means)

#np.save('/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/estimates/var_cov_v2023.npy',varcov)
np.save(r'C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1\estimates\var_cov_btm.npy',varcov)



