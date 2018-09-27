"""
This program simulates the model using the cleaned ACS data and parameter
estimates derived by the estimation files (2 & 3). It proceeds in multiple steps:

1. Simulate the leave type that is taken by each individual
2. Simulate the required probabilities for each binary decision
3. Simulate the binary decisions based on probabilities in step 2

6 March 2018
hautahi

To do:
- create the lnlength variable needed for input to
- simulate the decisions based on the binary probabilities
- figure out how to do this for multiple leaves
"""

# Housekeeping
import pandas as pd
import numpy as np

# Read in ACS data
d = pd.read_csv("./data/ACS_cleaned_forsimulation.csv")

# --------------
# 1. Simulate most recent leave type, which is taken to be the leave taken
# --------------

# Create a temporary "working" dataframe
df = d.copy()

## Calculate the probabilities for each leave type
leave_list = ["illchild","illparent","illspouse","matdis","bond","own"]

for leave in leave_list:
    
    # Load parameter estimates
    est = pd.read_csv("./estimates/typeleave_"+leave+".csv")
    x   = est['est'][0]
    
    # Compute the probability
    for i in range(1,est.shape[0]):
        x += df[est['var'][i]] * est['est'][i]
    df[leave+"_probtake"] = 1 / (1 + np.exp(-x))
    
# Get the sum of probabilities across all leave types (treating NA as zero)
cols = [col for col in df.columns if '_probtake' in col]
df['sum_probs'] = df[cols].sum(axis=1)

# Create probability for no leave
probs = 1 - df['sum_probs']
probs[probs<0] = 0
df["noleave_probtake"] = probs

# Normalize the probabilities
cols1 = cols + ["noleave_probtake"]
df['sum_probs'] = df[cols1].sum(axis=1)
for leave in leave_list:
    df[leave+"_probtake"] = df[leave+"_probtake"] / df['sum_probs']
    
# Create a list of each person's probabilities
prob_list = []
for leave in leave_list:
    prob_list.append(list(df[leave+"_probtake"]))
prob_list.append(df["noleave_probtake"])
prob_list = np.array(prob_list)
prob_list = np.transpose(prob_list)

# Make the multinomial random choice over leave types and assign to master dataframe
d["mostrecent"] = [np.random.choice(leave_list+["noleave"],p=p) for p in prob_list]

# ------------------------------------------------------
# 2. Simulate binary decision probabilities
# ------------------------------------------------------

"""
This section generates 6 columns for each decision (one for each leave type)
where the values in each column are the probability of a "yes" decision
"""

# Function to create binary decisions
def create_probs(df,ltype):

    for leave in leave_list:

        # Load parameter estimates
        est = pd.read_csv("./estimates/" + ltype +"_"+leave+".csv")
        x   = est['est'][0]

        # Compute the probability
        for i in range(1,est.shape[0]):
            x += df[est['var'][i]] * est['est'][i]
        df[leave+"_"+ltype] = 1 / (1 + np.exp(-x))
        
    return(df)

# Simulate seeing a doctor
d = create_probs(d,"seedoctor")

# Simulate probability of a hospital visit
d = create_probs(d,"hospvisit")

# Simulate probability of taking a leave conditional on needing one
d = create_probs(d,"takeleave")

# Simulate probability of receiving any pay
d = create_probs(d,"anypay")

# Simulate probability of fully paid leave (this needs the lnlength variable to be generated first)
#d = create_probs(d,"fullypaid")

# Simulate probability of taking a longer leave
d = create_probs(d,"longerleave")

# ------------------------------------------------------
# 3. Simulate binary decisions
# ------------------------------------------------------
