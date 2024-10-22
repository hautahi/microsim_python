
# Replicating CPS imputation via logistic regression of:
# 1.whether pay is received on an hourly basis; 
# 2. employer size; 
# 3. number of employers that the person worked for in the last 12 months; 
# 4. weekly pay (derived from weeks worked, separate regression not needed)
# 5. weeks worked 

# Housekeeping
import pandas as pd
import numpy as np
import patsy
from sklearn import linear_model
import warnings
#import mord as m

def load_cps(data):
    global df
    df = pd.read_csv(data)
        
def clean_cps(df):
    # data cleaning/var generation
    # strip out NIU/missing values (coded as '999'...)

    # Making zero/negative earnings into NaN so we can take natural log
    df['lnearn']=df['pearnval'].mask(df['pearnval'] <= 0, np.nan)
    df['lnearn']=np.log(df['lnearn'])
    # Making other values 0 per ACM code
    df.loc[(df['pearnval']<=0),'lnearn']=0


    #Create dummies for logit regressions
    df['female']=0
    df.loc[(df['a_sex']==2),'female']=1

    # Education dummies
    df['lths']=0
    df['somecol']=0
    df['ba']=0
    df['maplus']=0
    df.loc[(df['a_hga']<=38),'lths']=1
    df.loc[(df['a_hga']>=40) & (df['a_hga']<=42 ),'somecol']=1
    df.loc[(df['a_hga']==43),'ba']=1
    df.loc[(df['a_hga']>=44),'maplus']=1

    # Race/ethnicity dummies
    df['black']=0
    df['hispanic']=0
    df['asian']=0
    df['other']=0
    df.loc[(df['prdtrace']==2)&(df['pehspnon']==2),'black']=1
    df.loc[(df['prdtrace']==4)&(df['pehspnon']==2),'asian']=1
    df.loc[((df['prdtrace']==3)|((df['prdtrace']>=5)&(df['prdtrace']<=26)))&(df['pehspnon']==2),'other']=1
    df.loc[(df['pehspnon']==1),'hispanic']=1

    #age squared var
    df['agesq']=df['a_age']*df['a_age']

    #occupation and industry categories
    # hmm some missing are coded in with stata regressions
    df['occ_1']=0
    df['occ_2']=0
    df['occ_3']=0
    df['occ_4']=0
    df['occ_5']=0
    df['occ_6']=0
    df['occ_7']=0
    df['occ_8']=0
    df['occ_9']=0
    df['occ_10']=0
    df['maj_occ']=0
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_1']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_2']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_3']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_4']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_5']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_6']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_7']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_8']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_9']=np.nan
    df.loc[(df['a_mjocc']==0)|(df['a_mjocc']==11),'occ_10']=np.nan
    df.loc[(df['a_mjocc']==1), 'occ_1'] =1
    df.loc[(df['a_mjocc']==2), 'occ_2'] =1
    df.loc[(df['a_mjocc']==3), 'occ_3'] =1
    df.loc[(df['a_mjocc']==4), 'occ_4'] =1
    df.loc[(df['a_mjocc']==5), 'occ_5'] =1
    df.loc[(df['a_mjocc']==6), 'occ_6'] =1
    df.loc[(df['a_mjocc']==7), 'occ_7'] =1
    df.loc[(df['a_mjocc']==8), 'occ_8'] =1
    df.loc[(df['a_mjocc']==9), 'occ_9'] =1
    df.loc[(df['a_mjocc']==10), 'occ_10'] =1
    df['vmaj_occ']=0
    df.loc[df['maj_occ']>0,'vmaj_occ']=1

    df['ind_1']=0
    df['ind_2']=0
    df['ind_3']=0
    df['ind_4']=0
    df['ind_5']=0
    df['ind_6']=0
    df['ind_7']=0
    df['ind_8']=0
    df['ind_9']=0
    df['ind_10']=0
    df['ind_11']=0
    df['ind_12']=0
    df['ind_13']=0
    df['maj_ind']=0
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_1']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_2']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_3']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_4']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_5']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_6']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_7']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_8']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_9']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_10']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_11']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_12']=np.nan
    df.loc[(df['a_mjind']==0)|(df['a_mjind']==14),'ind_13']=np.nan
    
    df.loc[(df['a_mjind']==1), 'ind_1'] =1
    df.loc[(df['a_mjind']==2), 'ind_2'] =1
    df.loc[(df['a_mjind']==3), 'ind_3'] =1
    df.loc[(df['a_mjind']==4), 'ind_4'] =1
    df.loc[(df['a_mjind']==5), 'ind_5'] =1
    df.loc[(df['a_mjind']==6), 'ind_6'] =1
    df.loc[(df['a_mjind']==7), 'ind_7'] =1
    df.loc[(df['a_mjind']==8), 'ind_8'] =1
    df.loc[(df['a_mjind']==9), 'ind_9'] =1
    df.loc[(df['a_mjind']==10), 'ind_10'] =1
    df.loc[(df['a_mjind']==11), 'ind_11'] =1
    df.loc[(df['a_mjind']==12), 'ind_12'] =1
    df.loc[(df['a_mjind']==13), 'ind_13'] =1

    df['vmaj_ind']=0
    df.loc[df['maj_ind']>0,'vmaj_ind']=1

    df['paid_hrly']=np.nan
    df.loc[(df['prerelg']==1),'paid_hrly']=0
    df.loc[(df['prerelg']==1)&df['a_hrlywk']==1,'paid_hrly']=1
    
    df.loc[df['hiemp']==0,'hiemp']=np.nan
    df.loc[df['hiemp']==2,'hiemp']=0
    df.to_csv('data/Cleaned_CPS_for_regressions.csv', index=False)
    
def cps_logit_fit(dic,conditional, data):
    """
    This estimates logit regression coefficients from CPS
    dic:  dictionary of specifications
    d:    CPS dataset
    """
    for impute in dic:
        # Subset Data
        if conditional[impute]=="":
            d = data[:]
        else:    
            d = data[eval(conditional[impute])]
        y, X = patsy.dmatrices(dic[impute], d, return_type = 'dataframe')    
        
        # Get Weights          
        w = d['marsupwt'][X.index]
        
        # Run model
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
        global out_df
        out_df = pd.DataFrame(raw_data, columns=['var', 'est'])
        out_df.to_csv("./estimates/"+"CPS"+ "_" +impute + '.csv',index=False,header=True)
        print(out_df)

#===================
# Ordered logit on hold to see if R can do this
#===================

# def cps_ordered_logit_fit(dic,conditional, data):
#     """
#     This estimates ordered logit regression coefficients from CPS
#     dic:  dictionary of specifications
#     d:    CPS dataset
#     """
#     for impute in dic:
#         # Subset Data
#         if conditional[impute]=="":
#             d = data[:]
#         else:    
#             d = data[eval(conditional[impute])]
#         y, X = patsy.dmatrices(dic[impute], d, return_type = 'dataframe')    
        
#         # strip out intercept column
#         X=X.iloc[:,1:]
#         # Get Weights          
#         w = d['marsupwt'][X.index]
        
#         # Run model
#         clf = linear_model.LogisticRegression(solver='newton-cg', C=99999999)
#             # suppressing warnings generated from this, not concerning when we are just 
#             # looking for absolute replication of ACM at this point
#         warnings.filterwarnings("ignore")
#         clf.fit(X, y.values.ravel(), sample_weight = w)
#         warnings.filterwarnings("default")
        
#          # Save estimates to file
#         co_names = [x.split(")")[0] for x in list(X)]
#         co_names = [x.replace("C(","") for x in co_names]
#         raw_data = {'var': co_names, 'est': clf.coef_[0]}
#         out_df = pd.DataFrame(raw_data, columns=['var', 'est'])
#         out_df = out_df.append(pd.DataFrame(['Intercept'],columns=['var']), ignore_index=True)
#         out_df.iloc[len(co_names),0]=clf.intercept_
#         out_df.to_csv("./estimates/"+"CPS"+ "_" +impute + '.csv',index=False,header=True)

load_cps('data/CPS2014extract.csv')
clean_cps(df)

# #ordered logit for number of employers and weeks worked
# specif = {"num_employers":  "phmemprs ~ a_age + agesq + C(asian) + C(hispanic)"+
#           "+ C(lths) + C(somecol) + C(ba) + C(maplus) + C(lnearn)"+
#           "+ C(hiemp) + C(ind_4) + C(ind_5) + C(ind_6) + C(ind_8)"+
#           "+ C(ind_13) + C(occ_1) + C(occ_6) + C(occ_7) + C(occ_9)+ C(occ_10)"}
# cond = {"num_employers": ""}        
        
# logit for hourly paid regression
specif = {"paid_hrly":  "paid_hrly ~ C(female) + C(black) + a_age + agesq + C(ba)"
          + "+ C(maplus) + C(occ_1) + C(occ_3) + C(occ_5) + C(occ_7) + C(occ_8)"
          + "+ C(occ_9) + C(occ_10) + C(ind_5) + C(ind_8) + C(ind_11) + C(ind_12)"}  
cond = {"paid_hrly": ""}
cps_logit_fit(specif,cond,df)








