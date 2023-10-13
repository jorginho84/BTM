# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 12:51:16 2023

@author: Patricio De Araya
"""

import numpy as np
import pandas as pd
import sys, os
from scipy import stats
import math


class Utility(object):
    """
        This class defines the economic environment of the agents
    """
    
    
    def __init__(self,param,N,ecivil,children,X,psfe,year,educ,age,age_2):
        
        self.param = param
        self.N = N
        self.ecivil = ecivil
        self.children = children
        self.psfe = psfe
        # don't forget to definite X: characteristics
        self.X = X
        self.year = year
        self.educ = educ
        self.age = age
        self.age_2 = age_2
        
        
    #def economic_status(self,fps):
        
        #dc = 
        
        #prmti =
        
        #pe =
        
        #p eh =
        
        #pfse = 
        
        #return[pfse]
                
        
    def supply_salary(self):
        """
        Returns
        -------
        supply_salary : women's salary with shock.

        """
        
        number_w = self.N
        #agregar parámetro de varianza del shock, la varianza se estima,
        #la media es cero
        #np.random.multivariate_normal
        # Arreglar el shock (mean = 0)
        #normal, media cero, varianza parámetro
        shock_in = np.random.normal(0,self.param.gammas_x[4],(number_w))
        
        supply_salary = self.param.gammas_x[0] + self.educ*(self.param.gammas_x[1]) + \
            self.age*(self.param.gammas_x[2]) + self.age_2*(self.param.gammas_x[3])
        
        salaryv = supply_salary + shock_in
        #cambiar el código hacia adelante y dejar esto como x_0 = 1 , 1.2 1.05, 1.000111, 0.1
        #esto retorne ln 
        ln_salary = np.exp(salaryv)
        
        return ln_salary
    
    def btm_score(self):
        
        get_bonus = np.zeros(self.N)
        #acá la variable es menor o igual a cero
        get_bonus = np.where(((self.psfe<=98) & (self.year == 2012)) | ((self.psfe<=98) & (self.year == 2013)) | ((self.psfe<=104) & (self.year == 2014)) | 
                             ((self.psfe<=113) & (self.year == 2015)), 1, get_bonus)
        
        #modificar btm_score y btm_score_noise
        
        return get_bonus
        
    
    def btm_bonus(self,btm_score,supply_salary):
        """
        Parameters
        ----------
        supply_salary : salary.

        Returns
        -------
        btm : bonus amount.

        """
        
        ss_wlogbtm = supply_salary
        
        bonus = np.zeros(self.N)
        #salario anual
        bonus = np.where((ss_wlogbtm <= 222909), 0.2*ss_wlogbtm, bonus)
        bonus = np.where((222909 < ss_wlogbtm) & (ss_wlogbtm <= 278636), 0.2*222909, bonus)
        bonus = np.where((278636 < ss_wlogbtm) & (ss_wlogbtm <= 501545), 0.2*222909 - 0.2*(ss_wlogbtm-278636), bonus)
        
        btm = btm_score*bonus
        
        return btm
    
    
    def btm_noise(self):
        """
        focalization score with noise

        Returns
        -------
        false focalization score.

        """
        psfe_false = np.zeros(self.N)
        
        v_fs = np.random.normal(0, self.param.shocks[0], self.N)
        
        psfe_false = self.psfe + v_fs
        
        get_bonusf = np.zeros(self.N)
        #menor igual
        get_bonusf = np.where(((psfe_false<=98) & (self.year == 2012)) | ((psfe_false<=98) & (self.year == 2013)) | ((psfe_false<=104) & (self.year == 2014)) | 
                             ((psfe_false<=113) & (self.year == 2015)), 1, get_bonusf)
        
        return [get_bonusf, psfe_false]
    
    def btmfalse(self,btm_noise,supply_salary):
        """
        Parameters
        ----------
        psfe_false : score with noise.

        Returns
        -------
        bt with noise.

        """
        ss_wlogwbtm = supply_salary
        
        bonusf = np.zeros(self.N)
        #salario anual
        bonusf = np.where((ss_wlogwbtm <= 222909), 0.2*ss_wlogwbtm, bonusf)
        bonusf = np.where((222909 < ss_wlogwbtm) & (ss_wlogwbtm <= 278636), 0.2*222909, bonusf)
        bonusf = np.where((278636 < ss_wlogwbtm) & (ss_wlogwbtm <= 501545), 0.2*222909 - 0.2*(ss_wlogwbtm-278636), bonusf)
        
        btmf = btm_noise[0]*bonusf

        return btmf
        
       
    def income(self,work_d,supply_salary,btm_score,btm_bonus):
        """
        Parameters
        ----------
        work_d : women's decission.
        supply_salary : salary.
        btm : bonus amount.

        Returns
        -------
        Women's income.

        """
        supply_salaryIn = np.log(supply_salary)
        income = np.zeros(self.N)
        btm_score[work_d==0] = 0
        btm_bonus[btm_score==0] = 0
        
        btm_log = np.zeros_like(btm_bonus)
        
        idx = btm_bonus > 0
        
        np.log(btm_bonus, out=btm_log, where=idx)
        
        #np.where(btm_bonus == 0, 0, np.log(btm_bonus))
        
        for i in range(4):
            income = np.where((work_d == 1) & (btm_score == 1) & (self.ecivil == 1) & (self.children == i), self.param.mar_workload[0][i] + (supply_salaryIn*(self.param.mar_workload[1][i])) + btm_log, income)
            income = np.where((work_d == 1) & (btm_score == 1) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salaryIn*(self.param.dmar_workload[1][i])) + btm_log, income)
            income = np.where((work_d == 1) & (btm_score == 0) & (self.ecivil == 1) & (self.children == i), self.param.mar_workload[0][i] + (supply_salaryIn*(self.param.mar_workload[1][i])), income)
            income = np.where((work_d == 1) & (btm_score == 0) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salaryIn*(self.param.dmar_workload[1][i])), income)
            income = np.where((work_d == 0) & (btm_score == 0) & (self.ecivil == 1) & (self.children == i), self.param.dont_workload[0][i], income)
            income = np.where((work_d == 0) & (btm_score == 0) & (self.ecivil != 1) & (self.children == i), self.param.dont_workload[1][i], income)
            
            
            # ingreso total debe ir salary aunque no tenga btm
            #income = work_d*supply_salary + work_d*btm[0]
            #ingreso no laboral (pendiente)
            #decisión óptima, tomar o no tomar el btm (dummy: condicional en ser elegible)
            #Income = work_d*supply_salary + +btm[0]*work_d*btm[1] +ingreso_no_laboral + btm[0]*work_d*btm[1]*dummy_btm_choice*dummy_information
            #dummy information 
        
        return income
    
    def utility(self,income,work_d,btm_decision,btm_score):
        """
        Parameters
        ----------
        income : women's income.

        Returns
        -------
        Women's Utility.

        """
        
        utility = income - self.param.delta[0]*work_d - self.param.delta[1]*btm_decision*btm_score
        #restringir por la elegibilidad del btm optimo, btm_score

        
        return utility
    
        
                