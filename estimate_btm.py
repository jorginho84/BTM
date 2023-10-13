# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 13:42:51 2023

@author: Patricio De Araya
"""
from __future__ import division
import numpy as np
import pandas as pd
import pickle
import tracemalloc
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1")
import utility_btm as util
import parameters_btm as parameters
import simdata_btm as sd
import statsmodels.api as sm

class estimate:
    """
        This class estimates the model's parameters
    """
    
    def __init__(self,cutoff,educ,age,age_2,param0,N,ecivil,children,X,psfe,year,moments_vector, \
                 w_matrix):
        
        self.cutoff = cutoff
        self.educ = educ
        self.age = age
        self.age_2 = age_2 
        self.param0 = param0
        self.N = N
        self.ecivil = ecivil
        self.children = children
        self.psfe = psfe
        # don't forget to definite X: characteristics
        self.X = X
        self.year = year
        self.moments_vector = moments_vector
        self.w_matrix = w_matrix
        
        
    def simulation(self,times,modelSD):
        """
        Parameters
        ----------
        times : number.
        modelSD : model.

        Returns
        -------
        Parameters simulated.
        """
        
        emean_optwork = np.zeros(times)
        emean_optworkbtm = np.zeros(times)
        emean_optworkWbtm = np.zeros(times)
        emean_optincome = np.zeros(times)
        emean_elignot = np.zeros(times)
        emean_applynot = np.zeros(times)
        emean_scorequal = np.zeros(times)
        const_res = np.zeros(times)
        educ_res = np.zeros(times)
        age_res = np.zeros(times)
        age2_res = np.zeros(times)
        error_res = np.zeros(times)
        
        for i in range(1,times):
            
            np.random.seed(i+100)
            opt = modelSD.choice()
            
            df = {'OPTWORK': opt['Opt Work'], 'OPTBTM': opt['Opt BTM'], 'SSalary': opt['Supply Salary'],
                  'ELIG_NOT': opt['NEA MOMENT'], 'APPLY_NOT': opt['ENA MOMENT'], 'DISCONTINUITY': self.cutoff, 
                  'EDUCATION': self.educ, 'AGE': self.age, 'AGE_2': self.age_2}
            #me falta puntaje real de los datos
            datadf = pd.DataFrame(df, columns = ['OPTWORK','OPTBTM','OPTINCOME','ELIG_NOT','APPLY_NOT', 'SCORE EQUAL',
                                                 'DISCONTINUITY'])
            
            emean_optwork[i] = np.mean(np.array(datadf['OPTWORK']))
            emean_optworkbtm[i] = np.mean((datadf['OPTWORK'] == 1) & (datadf['OPTBTM'] == 1))
            emean_optworkWbtm[i] = np.mean((datadf['OPTWORK'] == 1) & (datadf['OPTBTM'] == 0))
            emean_elignot[i] = np.mean(np.array(datadf['ELIG_NOT']))
            emean_applynot[i] = np.mean(np.array(datadf['APPLY_NOT']))
            
            data_disc = datadf[(datadf['DISCONTINUITY'] >= -15) & (datadf['DISCONTINUITY'] <= 15)]
            data_disc = data_disc[data_disc['OPTWORK']== 1]
            # take up es btm_opt mean
            emean_scorequal[i] = np.mean((data_disc['OPTBTM']))
                
                
            data_reg = pd.DataFrame(df,columns = ['OPTWORK','SSalary', 'EDUCATION', 'AGE', 'AGE_2'])
            ## tomar ss, lo traigo desde return choice
            data_reg[data_reg['OPTWORK'] == 1]

            y = data_reg['SSalary']
            x = data_reg[['EDUCATION', 'AGE', 'AGE_2']]
            x = sm.add_constant(x)

            model_reg = sm.OLS(endog = y, exog = x)
            results = model_reg.fit()

            const_res[i] = results.params.const.round(8)
            educ_res[i] = results.params.EDUCATION.round(8)
            age_res[i] = results.params.AGE.round(8)
            age2_res[i] = results.params.AGE_2.round(8)
            error_res[i] = np.sqrt(results.scale)
            
            
        out_boots_work = np.mean(emean_optwork)
        out_boots_workbtm = np.mean(emean_optworkbtm)
        out_boots_workWbtm = np.mean(emean_optworkWbtm)
        out_boots_income = np.mean(emean_optincome)
        out_boots_elignot = np.mean(emean_elignot)
        out_boots_applynot = np.mean(emean_applynot)
        out_boots_scoreequal = np.mean(emean_scorequal)
        out_boots_const_res = np.mean(const_res)
        out_boots_educ_res = np.mean(educ_res)
        out_boots_age_res = np.mean(age_res)
        out_boots_age2_res = np.mean(age2_res)
        out_boots_error_res = np.mean(error_res)
        
        
        return {'Por opt work': out_boots_work,
                'Por opt work btm': out_boots_workbtm,
                'Por opt work W btm': out_boots_workWbtm,
                'Mean income': out_boots_income,
                'Por not eligible': out_boots_elignot,
                'Por not apply': out_boots_applynot,
                'Discontinuity': out_boots_scoreequal,
                'SS const': out_boots_const_res,
                'SS educ': out_boots_educ_res,
                'SS age': out_boots_age_res,
                'SS age_2': out_boots_age2_res,
                'SS error': out_boots_error_res}
    
    
    def objfunction(self,betas):
        """
        Parameters
        ----------
        betas : values calculated

        Returns
        -------
        Value function
        
        """
        
        self.param0.delta[0] = betas[0]
        self.param0.delta[1] = betas[1]
        self.param0.shocks[0] = betas[2]
        self.param0.shocks[1] = betas[3]
        self.param0.gammas_x[0] = betas[4]
        self.param0.gammas_x[1] = betas[5]
        self.param0.gammas_x[2] = betas[6]
        self.param0.gammas_x[3] = betas[7]
        self.param0.gammas_x[4] = betas[8]
        
        #momento varianza
        
        
        model = util.Utility(self.param0, self.N, self.ecivil, self.children, self.X, \
                             self.psfe, self.year,self.educ,self.age,self.age_2)
            
        modelSD = sd.SimData(self.param0, self.N, model)
        
        result = self.simulation(50,modelSD)
        
        betas_delta1 = result['Por opt work']
        betas_delta2 = result['Discontinuity']
        betas_notelig2 = result['Por not eligible']
        betas_shock_notapply = result['Por not apply']
        betas_gammas_x0 = result['SS const']
        betas_gammas_x1 = result['SS educ']
        betas_gammas_x2 = result['SS age']
        betas_gammas_x3 = result['SS age_2']
        betas_gammas_x4 = result['SS error']
        
        num_param = betas_delta1.size + betas_delta2.size + betas_notelig2.size + \
            betas_shock_notapply.size + betas_gammas_x0.size + betas_gammas_x1.size + \
                betas_gammas_x2.size + betas_gammas_x3.size + betas_gammas_x4.size
            
        x_vector = np.zeros((num_param,1))
        
        x_vector[0,0] = betas_delta1 - self.moments_vector[0]
        x_vector[2,0] = betas_delta2 - self.moments_vector[1]
        x_vector[1,0] = betas_notelig2 - self.moments_vector[2]
        x_vector[3,0] = betas_shock_notapply - self.moments_vector[3]
        x_vector[4,0] = betas_gammas_x0 - self.moments_vector[4]
        x_vector[5,0] = betas_gammas_x1 - self.moments_vector[5]
        x_vector[6,0] = betas_gammas_x2 - self.moments_vector[6]
        x_vector[7,0] = betas_gammas_x3 - self.moments_vector[7]
        x_vector[8,0] = betas_gammas_x3 - self.moments_vector[8]
        
        # Q metric
        q_w = np.dot(np.dot(np.transpose(x_vector),self.w_matrix),x_vector)
        
        print("")
        print("The objective function value equals ", q_w)
        print("")
        
        return q_w
    
    
    def optimizer(self):
        "Uses Nelder-Mead to optimize"
        
        beta0 = np.array([self.param0.delta[0],
                         self.param0.delta[1],
                         self.param0.shocks[0],
                         self.param0.shocks[1],
                         self.param0.gammas_x[0],
                         self.param0.gammas_x[1],
                         self.param0.gammas_x[2],
                         self.param0.gammas_x[3],
                         self.param0.gammas_x[4]])
        
        opt = minimize(self.objfunction, beta0,  method='Nelder-Mead', options={'maxiter':5000, 'maxfev': 90000, 'ftol': 1e-3, 'disp': True})
        
        return opt
        
        
        
        
            
            
            
        