# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:09:36 2023

@author: Patricio De Araya
"""

import numpy as np
import pandas as pd
import sys, os
sys.path.append("C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\btm_v1")
from openpyxl import Workbook 
from openpyxl import load_workbook

filename = 'C:/Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\Stata btm\casen2015\Results/param_python.xlsx'
df = pd.read_excel(filename, sheet_name = 'Python')

mar_worka = np.array(df['MarWorkA'])
mar_workb = np.array(df['MarWorkB'])
dmar_worka = np.array(df['DMarWorkA'])
dmar_workb = np.array(df['DMarWorkB'])
mar_dwork = np.array(df['MarDWork'])
dmar_dwork = np.array(df['SingleDWork'])

mar_work = [mar_worka, mar_workb]
dmar_work = [dmar_worka, dmar_workb]
dont_work = [mar_dwork, dmar_dwork]


np.save('mar_work_model.npy',np.array(mar_work, dtype=object), allow_pickle=True)
np.save('dmar_work_model.npy',np.array(dmar_work, dtype=object), allow_pickle=True)
np.save('dont_work_model.npy',np.array(dont_work, dtype=object), allow_pickle=True)
