"""
This program takes the cleaned FMLA data and calculates a number of
distirbutions of leave length.
"""

# Housekeeping
import pandas as pd
import numpy as np

# Define estimating function          
def get_dist(conditional,name):
    """
    This function creates a cdf for leave lengths
    """
    
    for leavetype in conditional:

        #print(leavetype)

        # Subset Data
        d1 = d[eval(conditional[leavetype])]
        
        # Get distribution
        temp = d1.groupby('length')['fixed_weight'].sum()
        out = temp.cumsum()/temp.sum()
        
        # Save estimates to file
        temp = {'length': np.array(out.index.values), 'cdf': np.array(out)}
        df = pd.DataFrame(temp)
        df.to_csv("./estimates/length_"+name+ "_" +leavetype + '.csv',index=False,header=True)

# Read in cleaned FMLA data
d = pd.read_csv("fmla_clean_2012.csv")

# --------------------------------------
# 1. Own health
# --------------------------------------

# subsetting data
conditional = {"noprog": "(d['take_own'] == 1) & (d['recStatePay'] == 0)",
               "prog": "(d['take_own'] == 1) & (d['recStatePay'] == 1)"}

get_dist(conditional,"ownhealth")

# --------------------------------------
# 2. Ill Child
# --------------------------------------

# subsetting data
conditional = {"male": "(d['take_illchild'] == 1) & (d['female'] == 0)",
               "female": "(d['take_illchild'] == 1) & (d['female'] == 1)"}

get_dist(conditional,"illchild")

# --------------------------------------
# 3. Ill Parent
# --------------------------------------

# subsetting data
conditional = {"male": "(d['take_illparent'] == 1) & (d['female'] == 0)",
               "female": "(d['take_illparent'] == 1) & (d['female'] == 1)"}

get_dist(conditional,"illparent")

# --------------------------------------
# 4. Ill Spouse
# --------------------------------------

# subsetting data
conditional = {"male": "(d['take_illspouse'] == 1) & (d['female'] == 0)",
               "female": "(d['take_illspouse'] == 1) & (d['female'] == 1)"}

get_dist(conditional,"illspouse")

# --------------------------------------
# 5. Maternity/Disability
# --------------------------------------

# subsetting data
conditional = {"only": "d['take_matdis'] == 1"}

get_dist(conditional,"maternity")

# --------------------------------------
# 6. New Child
# --------------------------------------

# subsetting data
conditional = {"male": "(d['take_bond'] == 1) & (d['female'] == 0)",
               "female": "(d['take_bond'] == 1) & (d['female'] == 1)"}

get_dist(conditional,"newchild")
