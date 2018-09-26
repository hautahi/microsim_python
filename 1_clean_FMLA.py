"""
This program takes the FMLA data and cleans it into a format to be used
for behavioral estimation
"""

# Housekeeping
import pandas as pd
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np

# Read in FMLA data
d = pd.read_csv("data/fmla_2012/fmla_2012_employee_restrict_puf.csv")

# FMLA eligible worker
d['eligworker'] = np.where((d['E13']==1) & ((d['E14'] == 1) | ((d['E15_CAT'] >= 5) & (d['E15_CAT'] <= 8))), 1, 0)
d['eligworker'] = np.where((np.isnan(d['E13'])) & (np.isnan(d['E14'])) & (np.isnan(d['E15_CAT'])), np.nan,d['eligworker'])

# Covered workplace
d['covwrkplace'] = np.where((d['E11']==1) | ((d['E12'] >= 6) & (d['E12'] <= 9)), 1, 0)
d['covwrkplace'] = np.where(np.isnan(d['covwrkplace']) , 0, d['covwrkplace'])
d['cond1']       = np.where(np.isnan(d['E11']) & np.isnan(d['E12']) , 1,0)
d['cond2']       = np.where((d['E11']==2) & (np.isnan(d['E11'])==False) & np.isnan(d['E12']),1,0)
d['miscond']     = np.where((d['cond1']==1) | (d['cond2']==1),1,0)
d['covwrkplace'] = np.where(d['miscond']==1,np.nan,d['covwrkplace'])

# Covered and eligible
d['coveligd'] = np.where((d['covwrkplace']==1) & (d['eligworker']==1) ,1,0)
d['coveligd'] = np.where(np.isnan(d['covwrkplace']) & np.isnan(d['eligworker']),np.nan,d['coveligd'])
d['coveligd'] = np.where(np.isnan(d['covwrkplace']) & (d['eligworker']==1),np.nan,d['coveligd'])
d['coveligd'] = np.where((d['covwrkplace']==1) & np.isnan(d['eligworker']),np.nan,d['coveligd'])

# Hourly worker
d['hourly'] = np.where(d['E9_1']==2,1,0)
d['hourly'] = np.where(np.isnan(d['E9_1']),np.nan,d['hourly'])

# Union member
d['union'] = np.where(d['D3']==1,1,0)
d['union'] = np.where(np.isnan(d['D3']),np.nan,d['union'])

# Employment Status
d['employed'] = np.where(d['E1']==1, 1, 0)
d['employed'] = np.where(np.isnan(d['E1']),np.nan,d['employed'])

# Hours per week
    # a dict to map code into average numeric hours per week
dict_wkhours = {
    1: 4,
    2: 11.5,
    3: 17,
    4: 21.5,
    5: 26.5,
    6: 32,
    7: 37.5,
    8: 45,
    'nan': np.nan
}
d['wkhours'] = d['E15_CAT_REV'].map(dict_wkhours)


# Employment at government
    # all rows should be valid for empgov_[] indicators, given FMLA sample
d['empgov_fed'] = np.where(d['D2']==1, 1, 0)
d['empgov_st'] = np.where(d['D2']==2, 1, 0)
d['empgov_loc'] = np.where(d['D2']==3, 1, 0)

# Age at midpoint of category
conditions = [(d['AGE_CAT'] == 1),(d['AGE_CAT'] == 2),
              (d['AGE_CAT'] == 3),(d['AGE_CAT'] == 4),
              (d['AGE_CAT'] == 5),(d['AGE_CAT'] == 6),
              (d['AGE_CAT'] == 7),(d['AGE_CAT'] == 8),
              (d['AGE_CAT'] == 9),(d['AGE_CAT'] == 10)]
choices = [21,27,32,37,42,47,52,57,63.5,70]
d['age']   = np.select(conditions, choices, default=np.nan)
d['agesq'] = np.array(d['age'])**2

# Sex
d['male']   = np.where(d['GENDER_CAT']==1,1,0)
d['female'] = np.where(d['GENDER_CAT']==2,1,0)

# No children
d['nochildren'] = np.where(d['D7_CAT']==0,1,0)
d['nochildren'] = np.where(np.isnan(d['D7_CAT']),np.nan,d['nochildren'])

# Number of dependents
d['ndep_kid'] = d.D7_CAT
d['ndep_old'] = d.D8_CAT

# Educational level
d['ltHS'] = np.where(d['D1_CAT']==1,1,0)
d['ltHS'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['ltHS'])

d['someHS'] = np.where(d['D1_CAT']==2,1,0)
d['someHS'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['someHS'])

d['HSgrad'] = np.where(d['D1_CAT']==3,1,0)
d['HSgrad'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['HSgrad'])

d['someCol'] = np.where(d['D1_CAT']==5,1,0)
d['someCol'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['someCol'])

d['BA'] = np.where(d['D1_CAT']==6,1,0)
d['BA'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['BA'])

d['GradSch'] = np.where(d['D1_CAT']==7,1,0)
d['GradSch'] = np.where(np.isnan(d['D1_CAT']),np.nan,d['GradSch'])

d['noHSdegree'] = np.where((d['ltHS']==1) | (d['someHS']==1),1,0)
d['noHSdegree'] = np.where(np.isnan(d['ltHS']) & np.isnan(d['someHS']),np.nan,d['noHSdegree'])

d['BAplus'] = np.where((d['BA']==1) | (d['GradSch']==1),1,0)
d['BAplus'] = np.where(np.isnan(d['BA']) & np.isnan(d['GradSch']),np.nan,d['BAplus'])

# Family income using midpoint of category
conditions = [(d['D4_CAT'] == 3),(d['D4_CAT'] == 4),
              (d['D4_CAT'] == 5),(d['D4_CAT'] == 6),
              (d['D4_CAT'] == 7),(d['D4_CAT'] == 8),
              (d['D4_CAT'] == 9),(d['D4_CAT'] == 10)]
choices = [15,25,32.5,37.5,45,62.5,87.5,130]
d['faminc'] = np.select(conditions, choices, default=np.nan)
d['lnfaminc'] = np.log(d['faminc'])

# Marital status
d['married'] = np.where(d['D10']==1,1,0)
d['married'] = np.where(np.isnan(d['D10']),np.nan,d['married'])

d['partner'] = np.where(d['D10']==2,1,0)
d['partner'] = np.where(np.isnan(d['D10']),np.nan,d['partner'])

d['separated'] = np.where(d['D10']==3,1,0)
d['separated'] = np.where(np.isnan(d['D10']),np.nan,d['separated'])

d['divorced'] = np.where(d['D10']==4,1,0)
d['divorced'] = np.where(np.isnan(d['D10']),np.nan,d['divorced'])

d['widowed'] = np.where(d['D10']==5,1,0)
d['widowed'] = np.where(np.isnan(d['D10']),np.nan,d['widowed'])

d['nevermarried'] = np.where(d['D10']==6,1,0)
d['nevermarried'] = np.where(np.isnan(d['D10']),np.nan,d['nevermarried'])

# Race/ethnicity
d['raceth'] = np.where((np.isnan(d['D5'])==False) & (d['D5']==1),7,d['D6_1_CAT'])

d['native'] = np.where(d['raceth']==1,1,0)
d['native'] = np.where(np.isnan(d['raceth']),np.nan,d['native'])

d['asian'] = np.where(d['raceth']==2,1,0)
d['asian'] = np.where(np.isnan(d['raceth']),np.nan,d['asian'])

d['black'] = np.where(d['raceth']==4,1,0)
d['black'] = np.where(np.isnan(d['raceth']),np.nan,d['black'])

d['white'] = np.where(d['raceth']==5,1,0)
d['white'] = np.where(np.isnan(d['raceth']),np.nan,d['white'])

d['other'] = np.where(d['raceth']==6,1,0)
d['other'] = np.where(np.isnan(d['raceth']),np.nan,d['other'])

d['hisp'] = np.where(d['raceth']==7,1,0)
d['hisp'] = np.where(np.isnan(d['raceth']),np.nan,d['hisp'])

# leave reason for most recent leave
d['reason_take'] = np.where((np.isnan(d['A20'])==False) & (d['A20']==2),d['A5_2_CAT'],d['A5_1_CAT'])

# leave reason for most recent leave (revised)
d['reason_take_rev'] = np.where((np.isnan(d['A20'])==False) & (d['A20']==2),d['A5_2_CAT_REV'],d['A5_1_CAT_rev'])

# taken doctor
d['YNdoctor_take'] = np.where((np.isnan(d['A20'])==False) & (d['A20']==2),d['A11_2'],d['A11_1'])
d['doctor_take']   = np.where(d['YNdoctor_take']==1,1,0)
d['doctor_take']   = np.where(np.isnan(d['YNdoctor_take']),np.nan,d['doctor_take'])

# taken hospital
d['YNhospital_take'] = np.where((np.isnan(d['A20'])==False) & (d['A20']==2),d['A12_2'],d['A12_1'])
d['hospital_take']   = np.where(d['YNhospital_take']==1,1,0)
d['hospital_take']   = np.where(np.isnan(d['YNhospital_take']),np.nan,d['hospital_take'])
d['hospital_take']   = np.where(np.isnan(d['hospital_take']) & (d['doctor_take']==0),0,d['hospital_take'])

# need doctor
d['doctor_need'] = np.where(d['B12_1']==1,1,0)
d['doctor_need'] = np.where(np.isnan(d['B12_1']),np.nan,d['doctor_need'])

# need hospital
d['hospital_need'] = np.where(d['B13_1']==1,1,0)
d['hospital_need'] = np.where(np.isnan(d['B13_1']),np.nan,d['hospital_need'])
d['hospital_need'] = np.where(np.isnan(d['hospital_need']) & (d['doctor_need']==0),0,d['hospital_need'])

# taken or needed doctor or hospital for leave category
d['doctor1'] = np.where((np.isnan(d['B13_1'])==False) & (d['LEAVE_CAT']==2),d['doctor_need'],d['doctor_take'])
d['doctor2'] = np.where((np.isnan(d['LEAVE_CAT'])==False) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==4)),d['doctor_need'],d['doctor_take'])

d['hospital1'] = np.where((np.isnan(d['LEAVE_CAT'])==False) & (d['LEAVE_CAT']==2),d['hospital_need'],d['hospital_take'])
d['hospital2'] = np.where((np.isnan(d['LEAVE_CAT'])==False) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==4)),d['hospital_need'],d['hospital_take'])

# length of leave for most recent leave
d['length']     = np.where((np.isnan(d['A20'])==False) & (d['A20']==2),d['A19_2_CAT_rev'],d['A19_1_CAT_rev'])
d['lengthsq']   = np.array(d['length'])**2
d['lnlength']   = np.log(d['length'])
d['lnlengthsq'] = np.log(d['length'])**2

# any pay received
d['anypay'] = np.where(d['A45']==1,1,0)
d['anypay'] = np.where(np.isnan(d['A45']),np.nan,d['anypay'])

# state program
d['recStateFL'] = np.where(d['A48b']==1,1,0)
d['recStateFL'] = np.where(np.isnan(d['A48b']),np.nan,d['recStateFL'])
d['recStateFL'] = np.where(np.isnan(d['recStateFL']) & (d['anypay']==0),0,d['recStateFL'])

d['recStateDL'] = np.where(d['A48c']==1,1,0)
d['recStateDL'] = np.where(np.isnan(d['A48c']),np.nan,d['recStateDL'])
d['recStateDL'] = np.where(np.isnan(d['recStateDL']) & (d['anypay']==0),0,d['recStateDL'])

d['recStatePay'] = np.where((d['recStateFL']==1) | (d['recStateDL']==1),1,0)
d['recStatePay'] = np.where(np.isnan(d['recStateFL']) | np.isnan(d['recStateDL']),np.nan,d['recStatePay'])

# fully paid
d['fullyPaid'] = np.where(d['A49']==1,1,0)
d['fullyPaid'] = np.where(np.isnan(d['A49']),np.nan,d['fullyPaid'])

# longer leave if more pay
d['longerLeave'] = np.where(d['A55']==1,1,0)
d['longerLeave'] = np.where(np.isnan(d['A55']),np.nan,d['longerLeave'])

# could not afford to take leave
d['unaffordable'] = np.where(d['B15_1_CAT']==5,1,0)
d['unaffordable'] = np.where(np.isnan(d['B15_1_CAT']),np.nan,d['unaffordable'])

# weights
w_emp             = np.mean(d[d['LEAVE_CAT'] == 3]['weight'])
w_leave           = np.mean(d[d['LEAVE_CAT'] != 3]['weight'])
d['fixed_weight'] = np.where(d['LEAVE_CAT']==3,w_emp,w_leave)
d['freq_weight']  = np.round(d['weight'])


# --------------------------
# dummies for leave type 
# --------------------------

# there are three variables for each leave type:
# (1) taking a leave
# (2) needing a leave
# (3) taking or needing a leave

# maternity disability
d['take_matdis'] = np.where(((d['A5_1_CAT']==21)&(d['A11_1']==1)&(d['GENDER_CAT']==2)) | (d['A5_1_CAT_rev']==32),1,0)
d['take_matdis'] = np.where(np.isnan(d['take_matdis']),0,d['take_matdis'])
d['take_matdis'] = np.where(np.isnan(d['A5_1_CAT']),np.nan,d['take_matdis'])
d['take_matdis'] = np.where(np.isnan(d['take_matdis']) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==3)),0,d['take_matdis'])

d['need_matdis'] = np.where(((d['B6_1_CAT']==21)&(d['B12_1']==1)&(d['GENDER_CAT']==2)) | (d['B6_1_CAT_rev']==32),1,0)
d['need_matdis'] = np.where(np.isnan(d['need_matdis']),0,d['need_matdis'])
d['need_matdis'] = np.where(np.isnan(d['B6_1_CAT']),np.nan,d['need_matdis'])
d['need_matdis'] = np.where(np.isnan(d['need_matdis']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_matdis'])

d['type_matdis'] = np.where((d['take_matdis']==1) | (d['need_matdis']==1),1,0)
d['type_matdis'] = np.where(np.isnan(d['take_matdis']) | np.isnan(d['need_matdis']),np.nan,d['type_matdis'])

# new child/bond
d['take_bond'] = np.where((d['A5_1_CAT']==21) & (np.isnan(d['A11_1']) | (d['GENDER_CAT']==1) | ((d['GENDER_CAT']==2) & (d['A11_1']==2) & (d['A5_1_CAT_rev']!=32))),1,0)
d['take_bond'] = np.where(np.isnan(d['A5_1_CAT']),np.nan,d['take_bond'])
d['take_bond'] = np.where(np.isnan(d['take_bond']) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==3)),0,d['take_bond'])

d['need_bond'] = np.where((d['B6_1_CAT']==21) & (np.isnan(d['B12_1']) | (d['GENDER_CAT']==1) | ((d['GENDER_CAT']==2) & (d['B12_1']==2) & (d['B6_1_CAT_rev']!=32))),1,0)
d['need_bond'] = np.where(np.isnan(d['B6_1_CAT']),np.nan,d['need_bond'])
d['need_bond'] = np.where(np.isnan(d['need_bond']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_bond'])

d['type_bond'] = np.where((d['take_bond']==1) | (d['need_bond']==1),1,0)
d['type_bond'] = np.where(np.isnan(d['take_bond']) | np.isnan(d['need_bond']),np.nan,d['type_bond'])

# own health
d['take_own'] = np.where(d['reason_take']==1,1,0)
d['take_own'] = np.where(np.isnan(d['take_own']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['take_own'])

d['need_own'] = np.where(d['B6_1_CAT']==1,1,0)
d['need_own'] = np.where(np.isnan(d['need_own']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_own'])

d['type_own'] = np.where((d['take_own']==1) | (d['need_own']==1),1,0)
d['type_own'] = np.where(np.isnan(d['take_own']) | np.isnan(d['need_own']),np.nan,d['type_own'])

#ill child
d['take_illchild'] = np.where(d['reason_take']==11,1,0)
d['take_illchild'] = np.where(np.isnan(d['take_illchild']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['take_illchild'])

d['need_illchild'] = np.where(d['B6_1_CAT']==11,1,0)
d['need_illchild'] = np.where(np.isnan(d['need_illchild']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_illchild'])

d['type_illchild'] = np.where((d['take_illchild']==1) | (d['need_illchild']==1),1,0)
d['type_illchild'] = np.where(np.isnan(d['take_illchild']) | np.isnan(d['need_illchild']),np.nan,d['type_illchild'])

#ill spouse
d['take_illspouse'] = np.where(d['reason_take']==12,1,0)
d['take_illspouse'] = np.where(np.isnan(d['take_illspouse']) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==3)),0,d['take_illspouse'])

d['need_illspouse'] = np.where(d['B6_1_CAT']==12,1,0)
d['need_illspouse'] = np.where(np.isnan(d['need_illspouse']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_illspouse'])

d['type_illspouse'] = np.where((d['take_illspouse']==1) | (d['need_illspouse']==1),1,0)
d['type_illspouse'] = np.where(np.isnan(d['take_illspouse']) | np.isnan(d['need_illspouse']),np.nan,d['type_illspouse'])

#ill parent
d['take_illparent'] = np.where(d['reason_take']==13,1,0)
d['take_illparent'] = np.where(np.isnan(d['take_illparent']) & ((d['LEAVE_CAT']==2) | (d['LEAVE_CAT']==3)),0,d['take_illparent'])

d['need_illparent'] = np.where(d['B6_1_CAT']==13,1,0)
d['need_illparent'] = np.where(np.isnan(d['need_illparent']) & ((d['LEAVE_CAT']==1) | (d['LEAVE_CAT']==3)),0,d['need_illparent'])

d['type_illparent'] = np.where((d['take_illparent']==1) | (d['need_illparent']==1),1,0)
d['type_illparent'] = np.where(np.isnan(d['take_illparent']) | np.isnan(d['need_illparent']),np.nan,d['type_illparent'])

# Save data
d.to_csv("data/fmla_clean_2012.csv", index=False, header=True)
