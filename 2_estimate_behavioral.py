"""
This program takes the cleaned FMLA data and runs a number of logit
regressions to produce coefficient estimates (which are stored as csv files)
to be used in the simulation model.
"""

# Housekeeping
import pandas as pd
import numpy as np
import patsy
from sklearn import linear_model
import warnings

# Define estimating function          
def logit_fit(dic,conditional,weights,d,name):
    """
    This estimates logit regressions and saves the estimates in csv files
    dic:  dictionary of specifications
    conditional:  dictionary of data conditionals
    d:    FMLA dataset
    name: str of decision name 
    """
    
    for leavetype in dic:

        #print(leavetype)

        # Subset Data
        if conditional[leavetype]=="":
            d1 = d[:]
        else:    
            d1 = d[eval(conditional[leavetype])]

        # Get matrices    
        y, X = patsy.dmatrices(dic[leavetype], d1, return_type = 'dataframe')    
        
        # Get Weights
        wt = weights[leavetype]
        if wt == "":
            w = None
        else:                
            w = d1[wt][X.index]
        
        # Run Logit Equation
        # Adding conditions from 2a_CPS estimate behaviors that corrected regressions there
        clf = linear_model.LogisticRegression(solver='newton-cg', C=99999999, fit_intercept=False)
        
        # suppressing warnings generated from this, not concerning when we are just 
        # looking for absolute replication of ACM at this point
        warnings.filterwarnings("ignore")
        clf.fit(X, y.values.ravel(), sample_weight = w)
        warnings.filterwarnings("default")
        
        # Save estimates to file
        co_names = [x.split(")")[0] for x in list(X)]
        co_names = [x.replace("C(","") for x in co_names]
        raw_data = {'var': co_names, 'est': clf.coef_[0]}
        print(name, leavetype,raw_data)
        df = pd.DataFrame(raw_data, columns=['var', 'est'])
        df.to_csv("./estimates/"+name+ "_" +leavetype + '.csv',index=False,header=True)

# Read in cleaned FMLA data
d = pd.read_csv("fmla_clean_2012.csv")

# --------------------
# 1. Type of leave taken
# --------------------

# Setup estimation equation dictionary
specif = {"own": "type_own ~ age + lnfaminc + C(hourly) + C(divorced) + C(coveligd)",
          "illspouse": "type_illspouse ~ age + agesq + C(widowed)",
          "illchild": "type_illchild ~ C(nochildren) + C(separated) + C(divorced)",
          "illparent": "type_illparent ~ age + agesq + C(male) + C(nevermarried) + C(BAplus)",
          "matdis": "type_matdis ~ age + lnfaminc",
          "bond": "type_bond ~ age + C(male) + lnfaminc + C(nevermarried)"
}

# subsetting data
conditional = {"own": "",
               "illspouse": "(d['nevermarried'] == 0) & (d['divorced'] == 0)",
               "illchild": "",
               "illparent": "",
               "matdis": "(d['female'] == 1) & (d['nochildren'] == 0)",
               "bond": "d['nochildren'] == 0"
}

weight = {"own": "fixed_weight",
          "illspouse": "fixed_weight",
          "illchild": "fixed_weight",
          "illparent": "weight",
          "matdis": "fixed_weight",
          "bond": "fixed_weight"
}

logit_fit(specif,conditional,weight,d,"typeleave")

# ------------------------------------------------------
# 2. Probability of seeing a doctor
# ------------------------------------------------------

# Specifications
specif = {"own": "doctor_take ~ age + C(male) + C(ltHS)",
          "illspouse":  "doctor_take ~ 1",
          "illchild":  "doctor_take ~ 1",
          "illparent":  "doctor_take ~ 1",
          "matdis":  "doctor_take ~ 1",
          "bond":  "doctor_take ~ 1"
}

# subsetting data
conditional = {"own": "d['take_own'] == 1",
               "illspouse": "d['take_illspouse'] == 1",
               "illchild": "d['take_illchild'] == 1",
               "illparent": "d['take_illparent'] == 1",
               "matdis": "d['take_matdis'] == 1",
               "bond": "d['take_bond'] == 1"
}

weight = {"own": "fixed_weight",
          "illspouse": "weight",
          "illchild": "weight",
          "illparent": "weight",
          "matdis": "weight",
          "bond": "weight"
}

logit_fit(specif,conditional,weight,d,"seedoctor")

# ------------------------------------------------------
# 3. Probability of Hospital Visit
# ------------------------------------------------------

# specifications
specif = {"own": "hospital_take ~ age + C(hourly)",
          "illspouse":  "hospital_take ~ 1",
          "illchild":  "hospital_take ~ 1",
          "illparent":  "hospital_take ~ 1",
          "matdis":  "hospital_take ~ 1",
          "bond":  "hospital_take ~ 1"}


# subsetting data
conditional = {"own": "(d['take_own'] == 1) & (d['doctor_take'] == 1)",
               "illspouse": "(d['take_illspouse'] == 1) & (d['doctor_take'] == 1)",
               "illchild": "(d['take_illchild'] == 1) & (d['doctor_take'] == 1)",
               "illparent": "(d['take_illparent'] == 1) & (d['doctor_take'] == 1)",
               "matdis": "(d['take_matdis'] == 1) & (d['doctor_take'] == 1)",
               "bond": "(d['take_bond'] == 1) & (d['doctor_take'] == 1)"}

# weights
weight = {"own": "weight",
          "illspouse": "weight",
          "illchild": "weight",
          "illparent": "weight",
          "matdis": "weight",
          "bond": "weight"}

logit_fit(specif,conditional,weight,d,"hospvisit")

# ---------------------------------------------------------------
# 4. Probability of taking a leave conditional on needing one
# ---------------------------------------------------------------

# specifications
specif = {"own": "take_own ~ age + C(male) + lnfaminc + C(black) + C(hisp) + C(coveligd)",
          "illspouse":  "take_illspouse ~ 1",
          "illchild":  "take_illchild ~ 1",
          "illparent":  "take_illparent ~ 1",
          "matdis":  "take_matdis ~ 1",
          "bond":  "take_bond ~ 1"}

# subsetting data
conditional = {"own": "d['type_own'] == 1",
               "illspouse": "d['type_illspouse'] == 1",
               "illchild": "d['type_illchild'] == 1",
               "illparent": "d['type_illparent'] == 1",
               "matdis": "d['type_matdis'] == 1",
               "bond": "d['type_bond'] == 1"}

# weights
weight = {"own": "weight",
          "illspouse": "weight",
          "illchild": "weight",
          "illparent": "weight",
          "matdis": "weight",
          "bond": "weight"}

logit_fit(specif,conditional,weight,d,"takeleave")

# ---------------------------------------------------------------
# 5. Probability of receiving any pay
# ---------------------------------------------------------------

# specifications
specif = {"own": "anypay ~ C(coveligd) + C(hourly) + age + agesq + lnfaminc",
          "illspouse":  "anypay ~ C(hourly)",
          "illchild":  "anypay ~ C(hourly)",
          "illparent":  "anypay ~ lnfaminc + C(hourly)",
          "matdis":  "anypay ~ lnfaminc",
          "bond":  "anypay ~ lnfaminc + C(coveligd)"}

# subsetting data
conditional = {"own": "d['take_own'] == 1",
               "illspouse": "d['take_illspouse'] == 1",
               "illchild": "d['take_illchild'] == 1",
               "illparent": "d['take_illparent'] == 1",
               "matdis": "d['take_matdis'] == 1",
               "bond": "d['take_bond'] == 1"}

# weights
weight = {"own": "",
          "illspouse": "fixed_weight",
          "illchild": "fixed_weight",
          "illparent": "fixed_weight",
          "matdis": "fixed_weight",
          "bond": "fixed_weight"}

logit_fit(specif,conditional,weight,d,"anypay")

# ---------------------------------------------------------------
# 6. Probability of fully paid leave 
# ---------------------------------------------------------------

# specifications
specif = {"own": "fullyPaid ~ C(hourly) + age + lnfaminc + lnlength",
          "illspouse":  "fullyPaid ~ lnfaminc",
          "illchild":  "fullyPaid ~ 1",
          "illparent":  "fullyPaid ~ lnfaminc",
          "matdis":  "fullyPaid ~ C(hourly) + lnlength",
          "bond":  "fullyPaid ~ lnlength"}

# subsetting data
conditional = {"own": "(d['take_own'] == 1) & (d['anypay'] == 1)",
               "illspouse": "(d['take_illspouse'] == 1) & (d['anypay'] == 1)",
               "illchild": "(d['take_illchild'] == 1) & (d['anypay'] == 1)",
               "illparent": "(d['take_illparent'] == 1) & (d['anypay'] == 1)",
               "matdis": "(d['take_matdis'] == 1) & (d['anypay'] == 1)",
               "bond": "(d['take_bond'] == 1) & (d['anypay'] == 1)"}

# weights
weight = {"own": "",
          "illspouse": "fixed_weight",
          "illchild": "weight",
          "illparent": "fixed_weight",
          "matdis": "fixed_weight",
          "bond": "fixed_weight"}

logit_fit(specif,conditional,weight,d,"fullypaid")

# ---------------------------------------------------------------
# 7. Probability of extend leave if any/additional pay
# ---------------------------------------------------------------

# specifications
specif = {"own": "longerLeave ~ age + agesq + female",
          "illspouse":  "longerLeave ~ age + coveligd",
          "illchild":  "longerLeave ~ 1",
          "illparent":  "longerLeave ~ 1",
          "matdis":  "longerLeave ~ 1",
          "bond":  "longerLeave ~ 1"}

# subsetting data
conditional = {"own": "d['take_own'] == 1",
               "illspouse": "d['take_illspouse'] == 1",
               "illchild": "d['take_illchild'] == 1",
               "illparent": "d['take_illparent'] == 1",
               "matdis": "d['take_matdis'] == 1",
               "bond": "d['take_bond'] == 1"}

# weights
weight = {"own": "fixed_weight",
          "illspouse": "fixed_weight",
          "illchild": "fixed_weight",
          "illparent": "fixed_weight",
          "matdis": "fixed_weight",
          "bond": "fixed_weight"}

logit_fit(specif,conditional,weight,d,"longerleave")

# ---------------------------------------------------------------
# 8. Proportion of Pay Received (ordered logit)
# ---------------------------------------------------------------

# specifications
specif = {"own": "C(A50) ~ 1",
          "matdis":  "C(A50) ~ lnlength",
          "bond":  "C(A50) ~ 1"}

# subsetting data
conditional = {"own": "(d['take_own'] == 1) & (d['fullyPaid'] == 0)",
               "matdis": "(d['take_matdis']) == 1 & (d['fullyPaid'] == 0)",
               "bond": "(d['take_bond'] == 1) & (d['fullyPaid'] == 0)"}

# Weights
weight = {"own": "fixed_weight",
          "matdis": "fixed_weight",
          "bond": "fixed_weight"}

######################
# Ordinal Logit Regression Required Here!
######################

# ---------------------------------------------------------------
# 9. Would take leave if pay available
# ---------------------------------------------------------------
# specifications
specif = {"own":"unaffordable ~ lnfaminc",
          "illspouse":"unaffordable ~ lnfaminc",
          "illchild":  "unaffordable ~ lnfaminc",
          "illparent":"unaffordable ~ lnfaminc",
          "matdis":"unaffordable ~ lnfaminc",
          "bond":"unaffordable ~ lnfaminc"}

# subsetting data
conditional = {"own": "d['need_own'] == 1",
               "illspouse": "d['need_illspouse'] == 1",
               "illchild": "d['need_illchild'] == 1",
               "illparent": "d['need_illparent'] == 1",
               "matdis": "d['need_matdis'] == 1",
               "bond": "d['need_bond'] == 1"}

# weights
weight = {"own":"fixed_weight",
          "illspouse":"fixed_weight",
          "illchild": "fixed_weight",
          "illparent":"fixed_weight",
          "matdis":"fixed_weight",
          "bond":"fixed_weight"}

logit_fit(specif,conditional,weight,d,"unaffordable")

# ---------------------------------------------------------------
# 10. Taking multiple leaves (ordered logit)
# ---------------------------------------------------------------

######################
# Ordinal Logit Regression Required Here!
######################

# Is there supposed to be an 11th regression here?  -Luke

