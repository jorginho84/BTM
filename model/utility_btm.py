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
    
    
    def __init__(self,param,N,ecivil,children):
        
        self.param = param
        self.N = N
        self.ecivil = ecivil
        self.children = children
        # don't forget to definite X: characteristics
        
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
        supply_salary : women's salary 
                with shock.

        """
        
        number_w = self.N
        #agregar parámetro de varianza del shock, la varianza se estima,
        #la media es cero
        shock_in = np.random.randn(number_w)
        
        supply_salary = self.X.dot(self.gammas_x) + shock_in
        
        e_salary = np.log(supply_salary)
        
        return e_salary
    
    
    def btm(self,psfe,year,supply_salary):
        """
        Parameters
        ----------
        psfe : socieconomic score.
        year : bonus year.
        supply_salary : salary.

        Returns
        -------
        btm : bonus amount.

        """
        
        get_bonus = np.zeros(self.N)
        #menor igual
        get_bonus = np.where(((psfe<=98) & (year == 2012)) | ((psfe<=98) & (year == 2013)) | ((psfe<=104) & (year == 2014)) | 
                             ((psfe<=113) & (year == 2015)), 1, get_bonus)
        
        bonus = np.zeros(self.N)
        #salario anual
        bonus = np.where((supply_salary <= 222909), 0.2*supply_salary, bonus)
        bonus = np.where((222909 < supply_salary) & (supply_salary <= 278636), 0.2*222909, bonus)
        bonus = np.where((278636 < supply_salary) & (supply_salary <= 501545), 0.2*222909 - 0.2*(supply_salary-278636), bonus)
        
        btm = get_bonus*bonus
        # np.log() ???
        return [btm, get_bonus]
    
    def information(self):
        """
        dummy information.

        Returns
        -------
        shock_information.

        """
        
        shock_information = np.random.binomial(1,self.param.s_info,self.N)
        
        return shock_information
    
    
    def income(self,work_d,supply_salary,btm,shock_information):
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
        btm[1][work_d==0] = 0
        btm[0][btm[1]==0] = 0
        
        for i in range(4):
            income = np.where((work_d == 1) & (btm[1] == 1) & (self.ecivil == 1) & (self.children == i), self.param.mar_workload[0][i] + (supply_salary*(self.param.mar_workload[1][i])) + shock_information*btm[0], income)
            income = np.where((work_d == 1) & (btm[1] == 1) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])) + shock_information*btm[0], income)
            income = np.where((work_d == 1) & (btm[1] == 0) & (self.ecivil == 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])) + shock_information*btm[0], income)
            income = np.where((work_d == 1) & (btm[1] == 0) & (self.ecivil != 1) & (self.children == i), self.param.dmar_workload[0][i] + (supply_salary*(self.param.dmar_workload[1][i])) + shock_information*btm[0], income)
            income = np.where((work_d == 0) & (btm[1] == 0) & (self.ecivil == 1) & (self.children == i), self.param.dont_workload[0][i] + btm[0], income)
            income = np.where((work_d == 0) & (btm[1] == 0) & (self.ecivil != 1) & (self.children == i), self.param.dont_workload[1][i] + btm[0], income)
            
            
            # ingreso total debe ir salary aunque no tenga btm
            #income = work_d*supply_salary + work_d*btm[0]
            #ingreso no laboral (pendiente)
            #decisión óptima, tomar o no tomar el btm (dummy: condicional en ser elegible)
            #Income = work_d*supply_salary + +btm[0]*work_d*btm[1] +ingreso_no_laboral + btm[0]*work_d*btm[1]*dummy_btm_choice*dummy_information
            #dummy information 
        
        return income
    
    def util(self,income,work_d,btm):
        """
        Parameters
        ----------
        income : women's income.

        Returns
        -------
        Women's Utility.

        """
        
        disuti_t1 = np.zeros(self.N)
        disuti_t3 = np.zeros(self.N)
       
        
        disuti_t1[np.logical_and(work_d == 1, btm[1] == 1)] = 1
        disuti_t3[np.logical_and(work_d == 1, btm[1] == 0)] = 1
        #costo directo, desutilidad (estigma)
        
        util = income - self.param.delta[0]*disuti_t1 - self.param.delta[2]*disuti_t3
        #si tomas el btm puede impacto negativo
        #Utility = ln(income) - alpha*dummy_trabajo - alpha2*dummy_btm_choice
        
        return util
    
        
                