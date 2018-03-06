#!/usr/bin/python3

"""
Tue 27 Feb 2018 02:14:37 PM PST

@author: aaron heuser

test_models.py
"""


import csv
import numpy as np
import pandas as pd


class ModelTest():
    """
    This class will import the test data and the associated model parameters,
    which is followed by a test of accuracy.
    """

    def __init__(self):
        """
        Parameters: None
        Returns:    None
        """

        # We first set the variables, for each type of regression, as in
        # Hautahi's code estimate_behavioral.py.
        self.specif, self.conditional = self.set_regression_variables()
        # Import the test data.
        self.data = pd.read_csv('fmla_clean_2012_test.csv')
        # Keep track of test accuracy.
        self.accuracy = {}
        self.size = {}
        for name in self.specif.keys():
            self.accuracy[name] = {}
            self.size[name] = {}
            for leavetype in self.specif[name].keys():
                accuracy, size = self.run_test(name, leavetype)
                self.accuracy[name][leavetype] = accuracy
                self.size[name][leavetype] = size
        self.write()

    def run_test(self, name, leavetype):
        """
        Parameters: name: str
                        The key in self.specif for which the test is to be
                        performed.
                    leavetype: str
                        The type of specification for this test.
        Returns:    accuracy: float
                        The result of the accuracy test
                    size: int
                        The number of data points off which this test is based.
        """

        # Generate the regression values.
        coefs, b, cols = self.gen_regression(name, leavetype)
        # Generate the test data
        test_data, observed = self.gen_test_data(cols, name, leavetype)
        # Determine the regression probability for each test value.
        if len(cols) > 0:
            probs = 1.0 / (1.0 + np.exp(-(b + np.dot(coefs, test_data))))
        else:
            probs = (1.0 / (1.0 + np.exp(-b))) * np.ones(len(observed))
        # Generate the predictions.
        predict = np.round(probs)
        # Get the indicies of non NaN elements.
        idx_nnan = [x for x in range(len(probs)) if not np.isnan(probs[x])]
        predict = np.array([predict[x] for x in idx_nnan])
        observed = np.array([observed[x] for x in idx_nnan])
        # True positive + true negative.
        tptn = sum(observed == predict)
        # Calculate accuracy.
        accuracy = tptn / len(observed)
        return accuracy, len(observed)

    def gen_regression(self, name, leavetype):
        """
        Parameters: name: str
                        The key in self.specif for which the regression is to
                        be generated.
                    leavetype: str
                        The key in self.specif[name] for which the
                        regression is to be generated.
        Returns:    coefs: array
                        The numpy array of regression coefficients.
                    b: float
                        The intercept.
                    cols: list
                        The list of variables that identify the columns needed.
        """

        coefs = []
        cols = []
        # Get the regression data.
        reg_data = pd.read_csv('./estimates/%s_%s.csv' % (name, leavetype))
        for row in reg_data.iterrows():
            if row[1]['var'].lower() == 'intercept':
                b = row[1]['est']
            else:
                coefs += [row[1]['est']]
                cols += [row[1]['var']]
        return np.array(coefs), b, cols

    def gen_test_data(self, cols, name, leavetype):
        """
        Parameters: cols: list
                        The list of data columns needed.
                    cond: str
                        The data conditional.
                    name: str
                        The key in self.specif for which the regression is to
                        be generated.
                    leavetype: str
                        The key in self.specif[name] for which the
                        regression is to be generated.
        Returns:    test_data: array
                        The matrix of test data values, where the order of the
                        columns is determined by cols.
                    observed: array
                        The array of observed outcomes.
        """

        test_data = []
        data = self.data.copy()
        if self.conditional[name][leavetype] != '':
            data = data[eval(self.conditional[name][leavetype])]
        # Having the conditional data, we take only what is needed.
        observed_text = self.specif[name][leavetype].split('~')[0].strip()
        observed = np.array(data[observed_text].tolist())
        # Some of the regressions have only an intercept, and so cols = []. In
        # this event, we return an array of zeros equal in length to observed.
        if len(cols) > 0:
            for col in cols:
                test_data += [data[col].tolist()]
        else:
            test_data = len(observed) * [0.0]
        return np.array(test_data), observed

    def write(self):
        """
        Parameters: None
        Returns:    None
        """

        # Output to file.
        with open('output_model_test.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'leavetype', 'accuracy', 'size'])
            for name in sorted(self.accuracy.keys()):
                for leavetype in sorted(self.accuracy[name].keys()):
                    accuracy = self.accuracy[name][leavetype]
                    size = self.size[name][leavetype]
                    writer.writerow([name, leavetype, accuracy, size])

    def set_regression_variables(self):
        """
        Parameters: None
        Returns:    specif: dict
                        The dictionary needed to specify regression variables.
                    conditional: dict
                        The conditional argument used to reduce data.
        """

        specif = {}
        conditional = {}
        observed = {}
        # We begin with the probability of taking leave.
        keys = ['own', 'illspouse', 'illchild', 'matdis', 'bond']
        v = 'type_own ~ age + lnfaminc + C(hourly) + C(divorced) + C(coveligd)'
        vals = [v]
        vals += ['type_illspouse ~ age + agesq + C(widowed)']
        vals += ['type_illchild ~ C(nochildren) + C(separated) + C(divorced)']
        vals += ['type_matdis ~ age + lnfaminc']
        vals += ['type_bond ~ age + C(male) + lnfaminc + C(nevermarried)']
        specif['takeleave'] = dict(zip(keys, vals))
        v1 = '(self.data["nevermarried"] == 0) & (self.data["divorced"] == 0)'
        vals = ['', v1, '', '']
        vals += ['(self.data["female"] == 1) & (self.data["nochildren"] == 0)'] 
        vals += ['self.data["nochildren"] == 0']
        conditional['takeleave'] = dict(zip(keys, vals))
        # The probability of seeing a doctor.
        vals = ['doctor_take ~ age + C(male) + C(ltHS)']
        vals += 5 * ['doctor_take ~ 1']
        specif['seedoctor'] = dict(zip(keys, vals))
        vals = ['self.data["take_own"] == 1']
        vals +=['self.data["take_illspouse"] == 1']
        vals += ['self.data["take_illchild"] == 1']
        vals += ['self.data["take_illparent"] == 1']
        vals += ['self.data["take_matdis"] == 1']
        vals += ['self.data["take_bond"] == 1']
        conditional['seedoctor'] = dict(zip(keys, vals))
        # The probability of a hospital visit.
        vals = ['hospital_take ~ age + C(hourly)']
        vals += 5 * ['hospital_take ~ 1']
        specif['hospvisit'] = dict(zip(keys, vals))
        v0 = '(self.data["take_own"] == 1) & (self.data["doctor_take"] == 1)'
        v1 = '(self.data["take_illspouse"] == 1) & '
        v1 += '(self.data["doctor_take"] == 1)'
        v2 = '(self.data["take_illchild"] == 1) & '
        v2 += '(self.data["doctor_take"] == 1)'
        v3 = '(self.data["take_illparent"] == 1) & '
        v3 += '(self.data["doctor_take"] == 1)'
        v4 = '(self.data["take_matdis"] == 1) & '
        v4 += '(self.data["doctor_take"] == 1)'
        v5 = '(self.data["take_bond"] == 1) & (self.data["doctor_take"] == 1)'
        vals = [v0, v1, v2, v3, v4, v5]
        conditional['hospvisit'] = dict(zip(keys, vals))
        # The probability of taking leave conditional on needing one.
        v0 = 'take_own ~ age + C(male) + lnfaminc + C(black) + C(hisp) + '
        v0 += 'C(coveligd)'
        vals = [v0]
        vals += ['take_illspouse ~ 1', 'take_illchild ~ 1']
        vals += ['take_illparent ~ 1', 'take_matdis ~ 1', 'take_bond ~ 1']
        specif['takeneedleave'] = dict(zip(keys, vals))
        vals = ['self.data["type_own"] == 1']
        vals += ['self.data["type_illspouse"] == 1']
        vals += ['self.data["type_illchild"] == 1']
        vals += ['self.data["type_illparent"] == 1']
        vals += ['self.data["type_matdis"] == 1']
        vals += ['self.data["type_bond"] == 1']
        conditional['takeneedleave'] = dict(zip(keys, vals))
        # The probability of receiving pay.
        vals = ['anypay ~ C(coveligd) + C(hourly) + age + agesq + lnfaminc']
        vals += ['anypay ~ C(hourly)', 'anypay ~ C(hourly)']
        vals += ['anypay ~ lnfaminc + C(hourly)', 'anypay ~ lnfaminc']
        vals += ['anypay ~ lnfaminc + C(coveligd)']
        specif['anypay'] = dict(zip(keys, vals))
        vals = ['self.data["type_own"] == 1']
        vals += ['self.data["type_illspouse"] == 1']
        vals += ['self.data["type_illchild"] == 1']
        vals += ['self.data["type_illparent"] == 1']
        vals += ['self.data["type_matdis"] == 1']
        vals += ['self.data["type_bond"] == 1']
        conditional['anypay'] = dict(zip(keys, vals))
        # The probability of fully paid leave.
        vals = ['fullyPaid ~ C(hourly) + age + lnfaminc + lnlength']
        vals += ['fullyPaid ~ lnfaminc', 'fullyPaid ~ 1']
        vals += ['fullyPaid ~ lnfaminc', 'fullyPaid ~ C(hourly) + lnlength']
        vals += ['fullyPaid ~ lnlength']
        specif['fullypaid'] = dict(zip(keys, vals))
        v1 = '(self.data["take_illspouse"] == 1) & (self.data["anypay"] == 1)'
        v2 = '(self.data["take_illchild"] == 1) & (self.data["anypay"] == 1)'
        v3 = '(self.data["take_illparent"] == 1) & (self.data["anypay"] == 1)'
        v4 = '(self.data["take_matdis"] == 1) & (self.data["anypay"] == 1)'
        v5 = '(self.data["take_bond"] == 1) & (self.data["anypay"] == 1)'
        vals = ['(self.data["take_own"] == 1) & (self.data["anypay"] == 1)']
        vals += [v1, v2, v3, v4, v5]
        conditional['fullypaid'] = dict(zip(keys, vals))
        # The probability of extended leave if any/additional pay.
        vals = ['longerLeave ~ age + agesq + female']
        vals += ['longerLeave ~ age + coveligd'] + 4 * ['longerLeave ~ 1']
        specif['longerleave'] = dict(zip(keys, vals))
        vals = ['self.data["type_own"] == 1']
        vals += ['self.data["type_illspouse"] == 1']
        vals += ['self.data["type_illchild"] == 1']
        vals += ['self.data["type_illparent"] == 1']
        vals += ['self.data["type_matdis"] == 1']
        vals += ['self.data["type_bond"] == 1']
        conditional['longerleave'] = dict(zip(keys, vals))
        return specif, conditional
