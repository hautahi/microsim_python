
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
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np

# -------------------------- #
# ACS Household File
# -------------------------- #

# Load data
st = 'ma'
d_hh = pd.read_csv("./data/acs/ss15h%s.csv" % st)

# Create Variables
d_hh["nochildren"]  = pd.get_dummies(d_hh["FPARC"])[4]
d_hh['faminc'] = d_hh['FINCP']*d_hh['ADJINC'] / 1042852 # adjust to 2012 dollars to conform with FMLA 2012 data
d_hh.loc[d_hh['faminc']<=0, 'faminc'] = 0.01 # force non-positive income to be epsilon to get meaningful log-income
d_hh["lnfaminc"]    = np.log(d_hh["faminc"])

# Number of dependents
d_hh['ndep_kid'] = d_hh.NOC
d_hh['ndep_old'] = d_hh.R65

# -------------------------- #
# ACS Personal File
# -------------------------- #

# Load data
d = pd.read_csv("./data/acs/ss15p%s.csv" % st)

# Merge with the household level variables
d = pd.merge(d,d_hh[['SERIALNO', 'nochildren', 'faminc','lnfaminc','PARTNER', 'ndep_kid', 'ndep_old']],
                 on='SERIALNO')

# Rename ACS variables to be consistent with FMLA data
rename_dic = {'AGEP': 'age'}
d.rename(columns=rename_dic, inplace=True)

# duplicating age column for meshing with CPS estimate output
d['a_age']=d['age']

# Create new ACS Variables
d['married'] = pd.get_dummies(d["MAR"])[1]
d["widowed"]        = pd.get_dummies(d["MAR"])[2]
d["divorced"]       = pd.get_dummies(d["MAR"])[3]
d["separated"]      = pd.get_dummies(d["MAR"])[4]
d["nevermarried"]   = pd.get_dummies(d["MAR"])[5]
    # use PARTNER in household data to override marital info in personal data
d['partner'] = 1 - pd.get_dummies(d['PARTNER'])[0] # PARTNER=0: no partner in household
for m in ['married', 'widowed', 'divorced', 'separated', 'nevermarried']:
    d.loc[d['partner']==1, m] = 0

d["male"]           = pd.get_dummies(d["SEX"])[1]
d["female"]         = 1 - d["male"]
d["agesq"]          = d["age"]**2

# Educational level
d['ltHS']    = np.where(d['SCHL']<=11,1,0)
d['someHS']  = np.where((d['SCHL']>=12) & (d['SCHL']<=15),1,0)
d['HSgrad']  = np.where((d['SCHL']>=16) & (d['SCHL']<=17),1,0)
d['someCol']  = np.where((d['SCHL']>=18) & (d['SCHL']<=20),1,0)
d["BA"]      = np.where(d['SCHL']==21,1,0)
d["GradSch"]  = np.where(d['SCHL']>=22,1,0)

d["noHSdegree"]  = np.where(d['SCHL']<=15,1,0)
d["BAplus"]  = np.where(d['SCHL']>=21,1,0)
    # variables for imputing hourly status, using CPS estimates from original model
d["maplus"]  = np.where(d['SCHL']>=22,1,0)
d["ba"]      = d['BA']

# race

d['white']= d['RAC1P'].apply(lambda x: int(x==1))
d['black']= d['RAC1P'].apply(lambda x: int(x==2))
d['asian']= d['RAC1P'].apply(lambda x: int(x==6))
d['hisp']= d['HISP'].apply(lambda x: int(x!=1))
d['other'] = d[['RAC1P', 'hisp']].apply(lambda x: int(x[0]!=1 and x[0]!=2 and x[0]!=6 and x[1]!=1), axis=1)

d['native'] = d['RAC1P'].apply(lambda x: int(x==3 or x==4 or x==5 or x==7))

# Employed
d['employed'] = np.where((d['ESR']== 1) |
                         (d['ESR'] == 2) |
                         (d['ESR'] == 4) |
                         (d['ESR'] == 5) ,
                         1, 0)
d['employed'] = np.where(np.isnan(d['ESR']),np.nan,d['employed'])

# Hours per week, total working weeks
d['wkhours'] = d['WKHP']
dict_wks = {
    1: 51,
    2: 48.5,
    3: 43.5,
    4: 33,
    5: 20,
    6: 7
}
d['wks'] = d['WKW'].map(dict_wks)

# Total wage past 12m, adjusted to 2012
d['wage12'] = d['WAGP'] *d['ADJINC'] / 1042852

# Employment at government
    # missing = age<16, or NILF over 5 years, or never worked
d['empgov_fed'] = np.where(d['COW']==5, 1, 0)
d['empgov_fed'] = np.where(np.isnan(d['COW']),np.nan,d['empgov_fed'])
d['empgov_st'] = np.where(d['COW']==4, 1, 0)
d['empgov_st'] = np.where(np.isnan(d['COW']),np.nan,d['empgov_st'])
d['empgov_loc'] = np.where(d['COW']==3, 1, 0)
d['empgov_loc'] = np.where(np.isnan(d['COW']),np.nan,d['empgov_loc'])


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
d.loc[d['OCCP10']=='N.A.', 'OCCP10'] = np.nan
d.loc[d['OCCP10'].isnull()==False, 'OCCP10'] = d.loc[d['OCCP10'].isnull()==False, 'OCCP10'].apply(lambda x: int(x))
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
    # d = d[(d['ESR'] == 1) | (d['ESR'] == 2)]

#  Restrict dataset to those that are not self-employed
    # d = d[(d['COW'] != 6) & (d['COW'] != 7)]

# -------------------------- #
# CPS Imputation
# -------------------------- #

"""
Not all the required behavioral independent variables are available
within the ACS. These therefore need to be imputed CPS

d["weeks_worked"] = 
d["weekly_earnings"] = 
"""

# These are just placeholders for now
# d["coveligd"] = np.nan
# d['union'] = np.nan

# adding in the prhourly worker imputation
# Double checked C++ code, and confirmed this is how they did hourly worker imputation.
hr_est=pd.read_csv('estimates/CPS_paid_hrly.csv').set_index('var').to_dict()['est']
d['prhourly']=0
for dem in hr_est.keys():
    if dem!='Intercept':
        d['prhourly']+=d[dem].fillna(0)*hr_est[dem]
d['prhourly']+=hr_est['Intercept']
d['prhourly']=np.exp(d['prhourly'])/(1+np.exp(d['prhourly']))
d['rand']=pd.Series(np.random.rand(d.shape[0]), index=d.index)
d['hourly']= np.where(d['prhourly']>d['rand'],1,0)
d=d.drop('rand', axis=1)

# -------------------------- #
# Save the resulting dataset
# -------------------------- #
cols = ['SERIALNO', 'PWGTP', 'ST',
'hourly',
'employed', 'empgov_fed','empgov_st','empgov_loc',
'wkhours', 'wks', 'wage12',
'age', 'agesq',
'male',
'nochildren', 'ndep_kid', 'ndep_old',
'ltHS', 'someHS', 'HSgrad', 'someCol', 'BA', 'GradSch', 'noHSdegree', 'BAplus' ,
'faminc', 'lnfaminc',
'married', 'partner', 'separated', 'divorced', 'widowed', 'nevermarried',
'native', 'asian', 'black', 'white', 'other', 'hisp',
'ESR', 'COW' # original ACS vars for restricting samples later
        ]
d_reduced = d[cols]
d_reduced.to_csv("./data/acs/ACS_cleaned_forsimulation_%s.csv" % st, index=False, header=True)

    # a wage only file for testing ABF
# d2 = d_reduced[['wage12','PWGTP']]
# d2.to_csv("./data/acs/ACS_cleaned_forsimulation_%s_wage.csv" % st, index=False, header=True)


