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
    
    
    def __init__(self,param,N,ecivil,children,X,psfe,year):
        
        self.param = param
        self.N = N
        self.ecivil = ecivil
        self.children = children
        self.psfe = psfe
        # don't forget to definite X: characteristics
        self.X = X
        self.year = year
    #def economic_status(self,fps):
        
        #dc = 
        
        #prmti =
        
        #pe =
        
        #peh =
        
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
        shock_in = np.random.randint(100000,500000,(number_w))
        
        supply_salary = self.X.dot(self.param.gammas_x) 
        
        e_salary = np.log(supply_salary) + shock_in
        
        return e_salary
    
    
    def btm_score(self):
        
        get_bonus = np.zeros(self.N)
        #menor igual
        get_bonus = np.where(((self.psfe<=98) & (self.year == 2012)) | ((self.psfe<=98) & (self.year == 2013)) | ((self.psfe<=104) & (self.year == 2014)) | 
                             ((self.psfe<=113) & (self.year == 2015)), 1, get_bonus)
        
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
        
        bonus = np.zeros(self.N)
        #salario anual
        bonus = np.where((supply_salary <= 222909), 0.2*supply_salary, bonus)
        bonus = np.where((222909 < supply_salary) & (supply_salary <= 278636), 0.2*222909, bonus)
        bonus = np.where((278636 < supply_salary) & (supply_salary <= 501545), 0.2*222909 - 0.2*(supply_salary-278636), bonus)
        
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
        
        v_fs = np.random.normal(0, self.param.sigma_foc_score, self.N)
        
        psfe_false = self.psfe + v_fs
        
        get_bonusf = np.zeros(self.N)
        #menor igual
        get_bonusf = np.where(((psfe_false<=98) & (self.year == 2012)) | ((psfe_false<=98) & (self.year == 2013)) | ((psfe_false<=104) & (self.year == 2014)) | 
                             ((psfe_false<=113) & (self.year == 2015)), 1, get_bonusf)
        
        return get_bonusf
    
    def btmfalse(self,btm_noise,supply_salary):
        """
        Parameters
        ----------
        psfe_false : score with noise.

        Returns
        -------
        bt with noise.

        """
        
        bonusf = np.zeros(self.N)
        #salario anual
        bonusf = np.where((supply_salary <= 222909), 0.2*supply_salary, bonusf)
        bonusf = np.where((222909 < supply_salary) & (supply_salary <= 278636), 0.2*222909, bonusf)
        bonusf = np.where((278636 < supply_salary) & (supply_salary <= 501545), 0.2*222909 - 0.2*(supply_salary-278636), bonusf)
        
        btmf = btm_noise*bonusf

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
        
        income = np.zeros(self.N)
        btm_score[work_d==0] = 0
        btm_bonus[btm_score==0] = 0
        
        for i in range(4):
            income = np.where((work_d == 1) & (btm_score == 1) & (self.ecivil == 1) & (self.children == i), self.param.mar_workload[0][i] + (supply_salary*(self.param.mar_workload[1][i])), income)
            income = np.where((work_d == 1) & (btm_score == 1) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])), income)
            income = np.where((work_d == 1) & (btm_score == 0) & (self.ecivil == 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])), income)
            income = np.where((work_d == 1) & (btm_score == 0) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])), income)
            income = np.where((work_d == 0) & (btm_score == 0) & (self.ecivil == 1) & (self.children == i), self.param.dont_workload[0][i] + btm_bonus, income)
            income = np.where((work_d == 0) & (btm_score == 0) & (self.ecivil != 1) & (self.children == i), self.param.dont_workload[1][i] + btm_bonus, income)
            
            
            # ingreso total debe ir salary aunque no tenga btm
            #income = work_d*supply_salary + work_d*btm[0]
            #ingreso no laboral (pendiente)
            #decisión óptima, tomar o no tomar el btm (dummy: condicional en ser elegible)
            #Income = work_d*supply_salary + +btm[0]*work_d*btm[1] +ingreso_no_laboral + btm[0]*work_d*btm[1]*dummy_btm_choice*dummy_information
            #dummy information 
        
        return income
    
    def utility(self,income,work_d,btm_decision):
        """
        Parameters
        ----------
        income : women's income.

        Returns
        -------
        Women's Utility.

        """
        #disuti_t0 = np.zeros(self.N)
        disuti_t1 = np.zeros(self.N)
        disuti_t3 = np.zeros(self.N)
       
        #disuti_t0[np.logical_and(work_d == 0, btm_decision == 0)] = 1
        disuti_t1[np.logical_and(work_d == 1, btm_decision == 1)] = 1
        disuti_t3[np.logical_and(work_d == 1, btm_decision == 0)] = 1
        #costo directo, desutilidad (estigma)
        
        utility = income - self.param.delta[0]*disuti_t1 - self.param.delta[2]*disuti_t3
        #si tomas el btm puede impacto negativo
        #Utility = ln(income) - alpha*dummy_trabajo - alpha2*dummy_btm_choice
        
        return utility
    
        
                