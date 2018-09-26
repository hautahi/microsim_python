# Source Python code for microsimulation model

This repository contains the code for the microsimulation project

- The `1_clean_FMLA.py` file takes the `data/fmla_2012/fmla_2012_employee_restrict_puf.csv` data as input, creates a number of variables required for the estimation procedures and saves the `data/fmla_clean_2012.csv` file.

- The `1a_get_response.py` file takes the `data/fmla_clean_2012.csv` data as input, creates a new column 'resp_length' to represent counterfactual leave length for FMLA workers in presence of a program

- (to be integrated later) The `2.estimate_behavioral.py` file taks the `data/fmla_clean_2012.csv` data as input and estimates a number of logit regressions. The resulting parameter estimates are saved as csv files in the `estimates` folder.

- (to be integrated later) The `2a_estimate_behavioral_cps` file does XYZ...

- (to be integrated later) The `3.estimate_distributions.py` file taks the `fmla_clean_2012.csv` data as input and calculates a number of leave length distributions, which is then saves as csv files in the `estimates` folder.

- The `4_clean_ACS.py` file takes the raw ACS files in the `data/acs` repository and creates the necessary variables to be consistent with the output from the estimation component and saves a master analysis data file called `ACS_cleaned_forsimulation.csv`.

- The `5_simulation_engine.py` file runs the simulation.

- The `5a_simulate_knn.py` file contains functions (knn) neeeded for simulation.

- (to be integrated later) The `5z_simulate_hk.py` file contains earilier simulation code by Hautahi Kingi.
