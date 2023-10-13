# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 12:57:53 2023

@author: Patricio De Araya
"""

class Parameters:
    """
        List of structural parameters
    """
    
    def __init__(self,gammas_x,mar_workload,dmar_workload,dont_workload,shocks,delta):
        
        self.gammas_x = gammas_x
        self.mar_workload = mar_workload
        self.dmar_workload = dmar_workload
        self.dont_workload = dont_workload
        self.shocks = shocks
        self.delta = delta