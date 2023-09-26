# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 13:42:51 2023

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
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1")
import utility_btm as util
import parameters_btm as parameters
import simdata_btm as sd

class estimate:
    """
        This class estimates the model's parameters
    """
    
    def __init__(self,cutoff,param0,N,ecivil,children,X,psfe,year,moments_vector, \
                 w_matrix):
        
        self.cutoff = cutoff
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
        
        for i in range(1,times):
            
            np.random.seed(i+100)
            opt = modelSD.choice()
            
            df = {'OPTWORK': opt['Opt Work'], 'OPTBTM': opt['Opt BTM'], 'OPTINCOME': opt['Opt Income'],
                  'ELIG_NOT': opt['NEA MOMENT'], 'APPLY_NOT': opt['ENA MOMENT'], 'SCORE EQUAL': opt['Equal score'],
                  'DISCONTINUITY': self.cutoff}
            #me falta puntaje real de los datos
            datadf = pd.DataFrame(df, columns = ['OPTWORK','OPTBTM','OPTINCOME','ELIG_NOT','APPLY_NOT', 'SCORE EQUAL',
                                                 'DISCONTINUITY'])
            
            emean_optwork[i] = np.mean(np.array(datadf['OPTWORK']))
            emean_optworkbtm[i] = np.mean((datadf['OPTWORK'] == 1) & (datadf['OPTBTM'] == 1))
            emean_optworkWbtm[i] = np.mean((datadf['OPTWORK'] == 1) & (datadf['OPTBTM'] == 0))
            emean_optincome[i] = np.mean(np.array(datadf['OPTINCOME']))
            emean_elignot[i] = np.mean(np.array(datadf['ELIG_NOT']))
            emean_applynot[i] = np.mean(np.array(datadf['APPLY_NOT']))
            
            data_disc = datadf[(datadf['DISCONTINUITY'] >= 0) & (datadf['DISCONTINUITY'] <= 15)]
            
            emean_scorequal[i] = np.mean(np.array(data_disc['SCORE EQUAL'] == 1)) 
            
            
        out_boots_work = np.mean(emean_optwork)
        out_boots_workbtm = np.mean(emean_optworkbtm)
        out_boots_workWbtm = np.mean(emean_optworkWbtm)
        out_boots_income = np.mean(emean_optincome)
        out_boots_elignot = np.mean(emean_elignot)
        out_boots_applynot = np.mean(emean_applynot)
        out_boots_scoreequal = np.mean(emean_scorequal)
        
        
        return {'Por opt work': out_boots_work,
                'Por opt work btm': out_boots_workbtm,
                'Por opt work W btm': out_boots_workWbtm,
                'Mean income': out_boots_income,
                'Por not eligible': out_boots_elignot,
                'Por not apply': out_boots_applynot,
                'Score equal': out_boots_scoreequal}
    
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
        
        
        model = util.Utility(self.param0, self.N, self.ecivil, self.children, self.X, \
                             self.psfe, self.year)
            
        modelSD = sd.SimData(self.param0, self.N, model)
        
        result = self.simulation(50,modelSD)
        
        betas_notelig1 = result['Por opt work']
        betas_notelig2 = result['Por not eligible']
        betas_shock_scoreequal = result['Score equal']
        betas_shock_notapply = result['Por not apply']
        
        num_param = betas_notelig1.size + betas_notelig2.size + betas_shock_scoreequal.size + \
            betas_shock_notapply.size
            
        x_vector = np.zeros((num_param,1))
        
        x_vector[0,0] = betas_notelig1 - self.moments_vector[0]
        x_vector[1,0] = betas_notelig2 - self.moments_vector[1]
        x_vector[2,0] = betas_shock_scoreequal - self.moments_vector[2]
        x_vector[3,0] = betas_shock_notapply - self.moments_vector[3]
        
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
                         self.param0.shocks[1]])
        
        opt = minimize(self.objfunction, beta0,  method='Nelder-Mead', options={'maxiter':5000, 'maxfev': 90000, 'ftol': 1e-3, 'disp': True})
        
        return opt
        
        
        
        
            
            
            
        