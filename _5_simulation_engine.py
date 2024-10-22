'''
Simulate leave taking behavior of ACS sample, using FMLA data

to do:
1. Need to think more about imputation to fill in missing values before kNN
2. Need to impute coveligd, more from ACM model
3. Need to compute counterfactual 'length' of leave for FMLA samples under new program

Chris Zhang 9/13/2018
'''

# -------------
# Housekeeping
# -------------

import pandas as pd
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np
from sklearn.neighbors import NearestNeighbors
import random
from _1a_get_response import get_response
from _5a_simulate_knn import simulate_knn

# -------------
# Read in Parameters
# -------------

# Algorithm parameter
k = 2

# State
st = 'ma'

# Variables to calculate distance function for knn
Xs = ['age','male','employed','wkhours','noHSdegree',
      'BAplus','empgov_fed', 'empgov_st', 'empgov_loc',
      'lnfaminc','black', 'asian', 'hisp', 'other',
      'ndep_kid', 'ndep_old','nevermarried', 'partner',
      'widowed', 'divorced', 'separated']

# replacement rate
rr = 0.25

# number of hours for fmla eligibility
hrs = 1250

# -------------
# Load Data
# -------------

# Read in the ACS data for the specified state
acs = pd.read_csv('./data/acs/ACS_cleaned_forsimulation_%s.csv' % st)

# -------------
# Simulate Counterfactual Leave
# -------------

# Create and save FMLA dataset with predicted counterfactual length of leave
# and read in the created dataset
outname='./data/fmla_clean_2012_resp_length.csv'
get_response(outname = outname)
fmla = pd.read_csv(outname)

# Simulate the predicted counterfactual length of leave in the ACS based
# on the value for the k nearest neighbors in the FMLA
acs['resp_length_full'] = simulate_knn(k, fmla, acs, Xs, 'resp_length')

# -------------
# Restrict ACS sample
# -------------

# Restrict based on employment status and age
acs = acs[(acs.age>=18)]
acs = acs.drop(index=acs[acs.ESR==4].index) # armed forces at work
acs = acs.drop(index=acs[acs.ESR==5].index) # armed forces with job but not at work
acs = acs.drop(index=acs[acs.ESR==6].index) # NILF
acs = acs.drop(index=acs[acs.COW==6].index) # self-employed, not incorporated
acs = acs.drop(index=acs[acs.COW==7].index) # self-employed, incoporated
acs = acs.drop(index=acs[acs.COW==8].index) # working without pay in family biz
acs = acs.drop(index=acs[acs.COW==9].index) # unemployed for 5+ years, or never worked

# Compute FMLA eligibility
acs['coveligd'] = 0

# set to 1 for all gov workers
acs.loc[acs['empgov_fed']==1, 'coveligd'] = 1
acs.loc[acs['empgov_st']==1, 'coveligd'] = 1
acs.loc[acs['empgov_loc']==1, 'coveligd'] = 1

# set to 1 for all workers with annual hours >= hrs
acs['yrhours'] = acs['wkhours'] * acs['wks']
acs.loc[acs['yrhours']>=hrs, 'coveligd'] = 1
del acs['yrhours']

# check wm-eligibility against FMLA
coveligd_wm_acs = sum(acs['coveligd']*acs['PWGTP']) / sum(acs['PWGTP'])
coveligd_wm_fmla = (fmla['coveligd']*fmla['freq_weight']).sum() / fmla[fmla.coveligd.isna()==False]['freq_weight'].sum()
x = coveligd_wm_acs/coveligd_wm_fmla
print('Estimated mean eligibility in ACS = %s times of mean eligibility in FMLA data' % round(x, 3))

# -------------
# Compute statistics based on the simulated variables above
# -------------

# daily wage
acs['wage1d'] = acs['wage12'] / acs['wks'] / 5
acs.loc[acs['wage12']==0, 'wage1d'] = 0 # hopefully this solves all missing wage1d cases

# total program cost
acs['cost_rep'] = acs['resp_length_full'] * acs['wage1d'] * acs['PWGTP'] * acs['coveligd'] * rr
TC = round(sum(acs['cost_rep'])/10**9, 3)
print('Method = kNN(k=%s), State = %s, Replacement rate = %s, Total Program Cost = $%s billion' % (k, st, rr, TC))
