# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 17:11:17 2023

@author: Patricio De Araya
"""

import numpy as np
import pandas as pd
import sys
import os
from scipy import stats
import math
from math import *
from scipy.optimize import minimize


class SimData:
    """

    """
    
    def __init__(self,param,N,model):
        """
        model: a utility instance (with arbitrary parameters)
        """
        
        self.param = param
        self.N = N
        self.model = model

        
        
    def util(self,work_d,btm_decision):
        """
        
        """
        #self y que no entre
        supply_salary = self.model.supply_salary()
        
        btm_score = self.model.btm_score()
        
        btm_bonus = self.model.btm_bonus(btm_score,supply_salary)
        
        btm_score_noise = self.model.btm_noise()
        
        btm_bonus_noise = self.model.btmfalse(btm_score_noise,supply_salary)
        
        #shock_information = self.model.information()
        
        income = self.model.income(work_d,supply_salary,btm_decision,btm_bonus)
        
        income_noise = self.model.income(work_d,supply_salary,btm_decision,btm_bonus_noise)
        
        # falta también, uno escogía tomar el btm
        # trabajar o no trabajar tomar o no el btm
        # generar btm decision

        
        return [self.model.utility(income,work_d,btm_decision), self.model.utility(income_noise,work_d,btm_decision), 
                btm_score, btm_score_noise]
    
    
    def choice(self):
        """
        
        """
        
        work_d1 = np.zeros(self.N)
        work_d2 = np.ones(self.N)
        btm_d1 = np.zeros(self.N)
        btm_d2 = np.ones(self.N)
        #3 opciones con btm 
        
        
        #todo con self
        u_0 = self.util(work_d1,btm_d1)
        u_1 = self.util(work_d2,btm_d1)
        u_3 = self.util(work_d2,btm_d2)
        
        #esto es la utilidad percibida, puntaje con ruido
        u_v2 = np.array([u_0[1], u_1[1], u_3[1]]).T
        u_v3 = np.array([u_v2[:,0], u_v2[:,1]]).T
        
        ###  Not eligible, applicants ###
        moment_nea = np.zeros(self.N)
        btm_score_opt = u_3[2]
        btm_noise_opt = u_3[3][0]
        
        moment_nea[np.logical_and(btm_score_opt == 0, btm_noise_opt == 1)] = 1
        
        ###  Not eligible, score btm == score btm noise ###
        moment_nesbsbn = np.zeros(self.N)
        moment_nesbsbn[np.logical_and(btm_score_opt == btm_noise_opt, btm_score_opt == 0)] = 1
        
        #option_opt = np.argmax(u_v2, axis=1)
        option_opt_si1 = np.argmax(u_v2, axis=1)
        option_opt_si0 = np.argmax(u_v3, axis=1)
        
        shock_info = self.param.shocks[1]
        shock_information = np.random.binomial(1,shock_info,self.N)

        option_opt_all = shock_information*option_opt_si1

        option_opt_all[np.logical_and(option_opt_all == 0, option_opt_si0 == 1)] = 1
        
        ### Eligible, not applicants ###
        btm_shockinfo_opt = np.zeros(self.N)
        btm_shockinfo_opt[np.logical_and(shock_information == 0, option_opt_si1 == 2)] = 1 
        
        work_opt = np.zeros(self.N)
        btm_opt = np.zeros(self.N)
        
        work_opt[option_opt_all==0]=0
        btm_opt[option_opt_all==0]=0
        work_opt[option_opt_all==1]=1
        btm_opt[option_opt_all==1]=0
        work_opt[option_opt_all==2]=1
        btm_opt[option_opt_all==2]=1
        # arreglar: aquí pasa a lo real
        # self y que no entre
        supply_salary = self.model.supply_salary()
        
        btm_score = self.model.btm_score()
        
        btm_bonus = self.model.btm_bonus(btm_score,supply_salary)
        
        #btm_score_noise = self.model.btm_noise()
        
        #btm_bonus_noise = self.model.btmfalse(btm_score_noise,supply_salary)
        
        #shock_information = self.model.information()
        
        income = self.model.income(work_opt,supply_salary,btm_opt,btm_bonus)
        
        #income_noise = self.model.income(work_opt,supply_salary,btm_opt,btm_bonus_noise,shock_information)
        
        utility_max = self.model.utility(income,work_opt,btm_opt)
        

                                
        return {'Opt Work': work_opt, 'Opt BTM': btm_opt, 'Opt Income': income,
                'Opt Utility': utility_max, 'NEA MOMENT': moment_nea, 'ENA MOMENT': btm_shockinfo_opt,
                'Equal score': moment_nesbsbn}