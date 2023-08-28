# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 21:27:57 2023

@author: Patricio De Araya
"""

#from __future__ import division #omit for python 3.x
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
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalTeacher\Local_teacher_profe_fit")
import time
import utility as util
import parameters as parameters
import simdata as sd
import estimate as est


np.random.seed(123)

#betas_nelder  = np.load("/Users/jorge-home/Dropbox/Research/teachers-reform/codes/teachers/betasopt_model_v22.npy")

#moments_vector = np.load("D:\Git\ExpSIMCE/moments.npy")

#data = pd.read_stata('D:\Git\ExpSIMCE/data_pythonpast.dta')
