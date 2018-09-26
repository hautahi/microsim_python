'''
simulator - knn

Chris Zhang 9/24/2018
'''

import pandas as pd
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np
from sklearn.neighbors import NearestNeighbors
import random
from _1a_get_response import get_params, get_wm_col

def simulate_knn(k, fmla, acs, Xs, var):
    '''

    :param k: k in knn
    :param fmla: fmla df, with response var column
    :param acs: acs df
    :param Xs: cols used for knn
    :param var: var of interest to be sourced from fmla
    :return: response var column for all acs ppl
    '''
    locs_fmla, locs_acs = fmla[Xs], acs[Xs] # locations of FMLA and ACS rows in space defined by knn_cols
        # impute missing values
    locs_fmla = locs_fmla.fillna(locs_fmla.mean())
    locs_acs = locs_acs.fillna(locs_acs.mean())
        # run kNN
    nbrs = NearestNeighbors(n_neighbors=k).fit(locs_fmla)
    distances, indices = nbrs.kneighbors(locs_acs)
    ns_nn = [len(pd.DataFrame(indices)[x].value_counts()) for x in range(k)]
    print('Number of FMLA workers found as 1st,..., %s-th, nearest neighbors = %s' % (k, ns_nn))
        # use kNN indices to merge with FMLA data
    for kk in range(k):
        acs['idx_nn%s' % kk] = pd.DataFrame(indices)[kk]
        fmla['idx_nn%s' % kk] = fmla.index # equivalent cols for merging
    for kk in range(k):
        acs = pd.merge(acs, fmla[['idx_nn%s' % kk, 'freq_weight', var]], how='left', on='idx_nn%s' % kk)
        acs.rename(columns={'freq_weight': 'w%s' % kk, var: '%s%s' % (var, kk)}, inplace=True)
        acs['%s%s' % (var, kk)] = acs['%s%s' % (var, kk)].fillna(0)
        # compute outvars to be simulated
    vws = []
    for kk in range(k):
        vws += [('%s%s' % (var, kk), 'w%s' % kk)]

        # Fully responsive length - if program is generous enough so that needers will have interior solutions
    var_for_acs = get_wm_col(acs, vws)

        # clean up resulting df
    acs = acs.drop(columns=['idx_nn%s' % kk for kk in range(k)] + [vw[0] for vw in vws] + [vw[1] for vw in vws])

    return var_for_acs
