'''
Simulate leave taking behavior of ACS sample, using FMLA data

to do:
1. Need to think more about imputation to fill in missing values before kNN
2. Need to impute coveligd, more from ACM model
3. Need to compute counterfactual 'length' of leave for FMLA samples under new program

Chris Zhang 9/13/2018
'''

import pandas as pd
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np
from sklearn.neighbors import NearestNeighbors
import random
from _1a_get_response import get_response
from _5a_simulate_knn import simulate_knn

# Algorithm parameter
k = 2

# State
st = 'ma'

# Data
get_response()
fmla = pd.read_csv('./data/fmla_clean_2012_resp_length.csv')
acs = pd.read_csv('./data/acs/ACS_cleaned_forsimulation_%s.csv' % st)

# kNN
k = 2
Xs = ['age',
            'male',
            'employed',
            'wkhours',
            'noHSdegree', 'BAplus',
            'empgov_fed', 'empgov_st', 'empgov_loc',
            'lnfaminc',
            'black', 'asian', 'hisp', 'other',
            'ndep_kid', 'ndep_old',
            'nevermarried', 'partner','widowed', 'divorced', 'separated']

acs['resp_length_full'] = simulate_knn(k, fmla, acs, Xs, 'resp_length')

# Compute total program cost
    # replacement rate
rr = 0.25
    # restrict to relevant persons in ACS
acs = acs[(acs.age>=18)]
acs = acs.drop(index=acs[acs.ESR==4].index) # armed forces at work
acs = acs.drop(index=acs[acs.ESR==5].index) # armed forces with job but not at work
acs = acs.drop(index=acs[acs.ESR==6].index) # NILF
acs = acs.drop(index=acs[acs.COW==6].index) # self-employed, not incorporated
acs = acs.drop(index=acs[acs.COW==7].index) # self-employed, incoporated
acs = acs.drop(index=acs[acs.COW==8].index) # working without pay in family biz
acs = acs.drop(index=acs[acs.COW==9].index) # unemployed for 5+ years, or never worked

    # FMLA eligibility
acs['coveligd'] = 0
        # set as 1 for all gov workers
acs.loc[acs['empgov_fed']==1, 'coveligd'] = 1
acs.loc[acs['empgov_st']==1, 'coveligd'] = 1
acs.loc[acs['empgov_loc']==1, 'coveligd'] = 1
        # set as 1 for all workers with annual hours >= 1250
acs['yrhours'] = acs['wkhours'] * acs['wks']
acs.loc[acs['yrhours']>=1250, 'coveligd'] = 1
del acs['yrhours']
        # check wm-eligibility against FMLA
coveligd_wm_acs = sum(acs['coveligd']*acs['PWGTP']) / sum(acs['PWGTP'])
coveligd_wm_fmla = (fmla['coveligd']*fmla['freq_weight']).sum() / fmla[fmla.coveligd.isna()==False]['freq_weight'].sum()
x = coveligd_wm_acs/coveligd_wm_fmla
print('Estimated mean eligibility in ACS = %s times of mean eligibility in FMLA data' % round(x, 3))

    # daily wage
acs['wage1d'] = acs['wage12'] / acs['wks'] / 5
acs.loc[acs['wage12']==0, 'wage1d'] = 0 # hopefully this solves all missing wage1d cases

    # total program cost
acs['cost_rep'] = acs['resp_length_full'] * acs['wage1d'] * acs['PWGTP'] * acs['coveligd'] * rr
TC = round(sum(acs['cost_rep'])/10**9, 3)
print('Method = kNN(k=%s), State = %s, Replacement rate = %s, Total Program Cost = $%s billion' % (k, st, rr, TC))


'''
vs = ['cost_rep','length','wage1d','PWGTP','coveligd']
vs = ['wage12', 'wks']
for v in vs:
    print(acs[v].isna().value_counts())

'''

