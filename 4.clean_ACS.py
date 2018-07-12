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

# Create new ACS Variables
d["widowed"]        = pd.get_dummies(d["MAR"])[2]
d["divorced"]       = pd.get_dummies(d["MAR"])[3]
d["separated"]      = pd.get_dummies(d["MAR"])[4]
d["nevermarried"]   = pd.get_dummies(d["MAR"])[5]
d["male"]           = pd.get_dummies(d["SEX"])[1]
d["female"]         = 1 - d["male"]
d["agesq"]          = d["age"]**2

# Educational level
d['ltHS']    = np.where(d['SCHL']<=15,1,0)
d["BA"]      = np.where(d['SCHL']==21,1,0)
d["BAplus"]  = np.where(d['SCHL']>=21,1,0)

# Educational level
d["black"]  = d['RACBLK']
d["hisp"]  = d['FHISP']

# -------------------------- #
# ACS Imputation
# -------------------------- #

"""
Not all the required behavioral independent variables are available
within the ACS. These therefore need to be imputed

d["weeks_worked"] = 
d["weekly_earnings"] = 
d["paid_hourly"] = 
"""

# These are just randomly generated placeholders for now
d["hourly"] = np.random.randint(2, size=d.shape[0])
d["coveligd"] = np.random.randint(2, size=d.shape[0])

# -------------------------- #
# Remove ineligible workers
# -------------------------- #

# Restrict dataset to civilian employed workers (check this)
d = d[(d['ESR'] == 1) | (d['ESR'] == 2)]

#  Restrict dataset to those that are not self-employed
d = d[(d['COW'] != 6) & (d['COW'] != 7)]

# -------------------------- #
# Save the resulting dataset
# -------------------------- #

d.to_csv("./data/ACS_cleaned_forsimulation.csv", index=False, header=True)
