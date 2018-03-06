#!/usr/bin/python3

"""
Tue 27 Feb 2018 11:40:19 AM PST

@author: aaron heuser

separate_data.py
"""


import numpy as np
import pandas as pd


class SeparateData():
    """
    This class is used to randomly (uniform) separate the cleaned data into two
    equal subsets.
    """

    def __init__(self):
        """
        Parameters: None
        Returns:    None
        """

        # Import the data.
        data = pd.read_csv('../microsim_python-master/fmla_clean_2012.csv')
        # Assign each row into either group 0 or group 1. We begin by
        # determining the count of each.
        train_size = int(len(data) / 2)
        rng = range(len(data))
        train_range = sorted(np.random.choice(rng, train_size, replace=False))
        test_range = [x for x in rng if x not in train_range]
        data_train = data.iloc[train_range, :].reset_index(drop=True)
        data_test = data.iloc[test_range, :].reset_index(drop=True)
        # Write to files.
        data_train.to_csv('fmla_clean_2012_train.csv', index=False)
        data_test.to_csv('fmla_clean_2012_test.csv', index=False)


def main():
    """
    Parameters: None
    Returns:    None
    """

    sd = SeparateData()

if __name__ == '__main__':
    main()
