import statsmodels.api as sm
import pandas as pd


# The dependent variables and their explanatory variables need to be given here!!
# For example: fields = {'take_leave': ['age', 'income'], 'want_leave': ['gender', 'age'], ...}
fields = {}

def fit(data):
    for f in fields:
        logit = sm.Logit(data[f], data[fields[f]]).fit()
        raw_data = {'variables': fields[f], 'coefficients': logit.params.values}
        data_frame = pd.DataFrame(raw_data, columns=['variables', 'coefficients'])
        data_frame.to_csv(f + '.csv', index=False, header=None)