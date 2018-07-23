
"""
This program loads in the raw ACS files, creates the necessary variables
for the simulation and saves a master dataset to be used in the simulations.

2 March 2018
hautahi

To do:
- The biggest missing piece is the imputation of ACS variables using the CPS. These are currently just randomly generated.
- Check if the ACS variables are the same as those in the C++ code

"""

# -------------------------- #
# Housekeeping
# -------------------------- #

import pandas as pd
import numpy as np

# -------------------------- #
# ACS Household File
# -------------------------- #

# Load data
d_hh = pd.read_csv("./data/ss15hma_short.csv")

# Create Variables
d_hh["nochildren"]  = pd.get_dummies(d_hh["FPARC"])[4]
d_hh["lnfaminc"]    = np.log(d_hh["FINCP"])

# -------------------------- #
# ACS Personal File
# -------------------------- #

# Load data
d = pd.read_csv("./data/ss15pma_short.csv")

# Merge with the household level variables
d = pd.merge(d,d_hh[['SERIALNO', 'nochildren', 'lnfaminc']],
                 on='SERIALNO')

# Rename ACS variables to be consistent with FMLA data
rename_dic = {'AGEP': 'age'}
d.rename(columns=rename_dic, inplace=True)

# duplicating age column for meshing with CPS estimate output
d['a_age']=d['age']

# Create new ACS Variables
d["widowed"]        = pd.get_dummies(d["MAR"])[2]
d["divorced"]       = pd.get_dummies(d["MAR"])[3]
d["separated"]      = pd.get_dummies(d["MAR"])[4]
d["nevermarried"]   = pd.get_dummies(d["MAR"])[5]
d["male"]           = pd.get_dummies(d["SEX"])[1]
d["female"]         = 1 - d["male"]
d["agesq"]          = d["age"]**2

# Educational level
d['lths']    = np.where(d['SCHL']<=15,1,0)
d['somcol']  = np.where((d['SCHL']>=18) & (d['SCHL']<=20),1,0)
d["ba"]      = np.where(d['SCHL']==21,1,0)
d["baplus"]  = np.where(d['SCHL']>=21,1,0)
d["maplus"]  = np.where(d['SCHL']>=22,1,0)

# race
d['black']= d.loc[d['RAC1P']==2, 'RAC1P']
d['asian']= d.loc[d['RAC1P']==6, 'RAC1P']
d['other race']= d.loc[d['RAC1P']!=1, 'RAC1P']
d['hispanic']= d.loc[d['HISP']>1, 'HISP']

# Occupation
d['occ_1']=0
d['occ_2']=0
d['occ_3']=0
d['occ_4']=0
d['occ_5']=0
d['occ_6']=0
d['occ_7']=0
d['occ_8']=0
d['occ_9']=0
d['occ_10']=0
d['maj_occ']=0
d.loc[(d['OCCP10']>=10) & (d['OCCP10']<=950), 'occ_1'] =1
d.loc[(d['OCCP10']>=1000) & (d['OCCP10']<=3540), 'occ_2'] =1
d.loc[(d['OCCP10']>=3600) & (d['OCCP10']<=4650), 'occ_3'] =1
d.loc[(d['OCCP10']>=4700) & (d['OCCP10']<=4965), 'occ_4'] =1
d.loc[(d['OCCP10']>=5000) & (d['OCCP10']<=5940), 'occ_5'] =1
d.loc[(d['OCCP10']>=6000) & (d['OCCP10']<=6130), 'occ_6'] =1
d.loc[(d['OCCP10']>=6200) & (d['OCCP10']<=6940), 'occ_7'] =1
d.loc[(d['OCCP10']>=7000) & (d['OCCP10']<=7630), 'occ_8'] =1
d.loc[(d['OCCP10']>=7700) & (d['OCCP10']<=8965), 'occ_9'] =1
d.loc[(d['OCCP10']>=9000) & (d['OCCP10']<=9750), 'occ_10'] =1

# Industry
d['ind_1']=0
d['ind_2']=0
d['ind_3']=0
d['ind_4']=0
d['ind_5']=0
d['ind_6']=0
d['ind_7']=0
d['ind_8']=0
d['ind_9']=0
d['ind_10']=0
d['ind_11']=0
d['ind_12']=0
d['ind_13']=0
d.loc[(d['INDP']>=170) & (d['INDP']<=290), 'ind_1'] =1
d.loc[(d['INDP']>=370) & (d['INDP']<=490), 'ind_2'] =1
d.loc[(d['INDP']==770), 'ind_3'] =1
d.loc[(d['INDP']>=1070) & (d['INDP']<=3990), 'ind_4'] =1
d.loc[(d['INDP']>=4070) & (d['INDP']<=5790), 'ind_5'] =1
d.loc[((d['INDP']>=6070) & (d['INDP']<=6390))|((d['INDP']>=570) & (d['INDP']<=690)), 'ind_6'] =1
d.loc[(d['INDP']>=6470) & (d['INDP']<=6780), 'ind_7'] =1
d.loc[(d['INDP']>=6870) & (d['INDP']<=7190), 'ind_8'] =1
d.loc[(d['INDP']>=7270) & (d['INDP']<=7790), 'ind_9'] =1
d.loc[(d['INDP']>=7860) & (d['INDP']<=8470), 'ind_10'] =1
d.loc[(d['INDP']>=8560) & (d['INDP']<=8690), 'ind_11'] =1
d.loc[(d['INDP']>=8770) & (d['INDP']<=9290), 'ind_12'] =1
d.loc[(d['INDP']>=9370) & (d['INDP']<=9590), 'ind_13'] =1

# -------------------------- #
# Remove ineligible workers
# -------------------------- #

# Restrict dataset to civilian employed workers (check this)
d = d[(d['ESR'] == 1) | (d['ESR'] == 2)]

#  Restrict dataset to those that are not self-employed
d = d[(d['COW'] != 6) & (d['COW'] != 7)]

# -------------------------- #
# CPS Imputation
# -------------------------- #

"""
Not all the required behavioral independent variables are available
within the ACS. These therefore need to be imputed CPS

d["weeks_worked"] = 
d["weekly_earnings"] = 
"""

# These are just randomly generated placeholders for now
d["coveligd"] = np.random.randint(2, size=d.shape[0])

# adding in the prhourly worker imputation
# Double checked C++ code, and confirmed this is how they did hourly worker imputation.
hr_est=pd.read_csv('estimates/CPS_paid_hrly.csv').set_index('var').to_dict()['est']
d['prhourly']=0
for dem in hr_est.keys():
    if dem!='intercept':
        d['prhourly']+=d[dem].fillna(0)*hr_est[dem]
d['prhourly']+=hr_est['intercept']
d['prhourly']=np.exp(d['prhourly'])/(1+np.exp(d['prhourly']))
d['rand']=pd.Series(np.random.rand(d.shape[0]), index=d.index)
d['hourly']= np.where(d['prhourly']>d['rand'],1,0)
d=d.drop('rand', axis=1)

# -------------------------- #
# Save the resulting dataset
# -------------------------- #

d.to_csv("./data/ACS_cleaned_forsimulation.csv", index=False, header=True)
