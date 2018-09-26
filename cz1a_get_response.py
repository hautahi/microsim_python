'''
get response of leave taking in presence of new program

To do: need a hyperparameter alpha to capture effect of program generosity (replacement rate) on response length

can use California data (with current replacement > 0) to calibrate

Chris Zhang 9/20/2018
'''

import pandas as pd
pd.set_option('display.max_columns', 999)
pd.set_option('display.width', 200)
import numpy as np
from sklearn.neighbors import NearestNeighbors

# a function to prepare data
def set_data(df):
    '''

    :param df: fmla_clean_2012.csv
    :return:
    '''
    ## Set index to uniquely identify workers
    df = df.set_index('empid')

    ## fillna for current leave length
    df['length'] = df[['LEAVE_CAT', 'length']].groupby('LEAVE_CAT').transform(lambda x: x.fillna(x.mean()))

    ## Consider a program which increases wage replacement
        # a column to flag 0/1 for any response with increase in leave length
    df['resp_len'] = np.nan
        # LEAVE_CAT: employed only
    df.loc[df['LEAVE_CAT']==3, 'resp_len'] = 0
        # A55: would take longer if paid?
    df.loc[(df['resp_len'].isna()) & (df['A55']==2), 'resp_len'] = 0
    df.loc[(df['resp_len'].isna()) & (df['A55']==1), 'resp_len'] = 1
        # A23c: unable to afford unpaid leave due to leave taking
        # A53g: cut leave time short to cover lost wages
        # A62a: return to work because cannot afford more leaves
        # B15_1_CAT, B15_2_CAT: can't afford unpaid leave
    df.loc[(df['resp_len'].isna()) & ((df['A23c']==1) |
                               (df['A53g']==1) |
                               (df['A62a']==1) |
                               (df['B15_1_CAT']==5) |
                               (df['B15_2_CAT']==5)), 'resp_len'] = 1
        # A10_1, A10_2: regular/ongoing condition, takers and dual
        # B11_1, B11_2: regular/ongoing condition, needers and dual
    df.loc[(df['resp_len'].isna()) & (df['A10_1']==2) | (df['A10_1']==3)
           | (df['B11_1']==2) | (df['B11_1']==3), 'resp_len'] = 1
        # Check reasons of no leave among rest: df[df['resp_len'].isna()].B15_1_CAT.value_counts().sort_index()
        # all reasons unsolved by replacement generosity
    df.loc[(df['resp_len'].isna()) & (df['B15_1_CAT'].notna()), 'resp_len'] = 0
    df.loc[(df['resp_len'].isna()) & (df['B15_2_CAT'].notna()), 'resp_len'] = 0
        # Check LEAVE_CAT of rest: df[df['resp_len'].isna()]['LEAVE_CAT'].value_counts().sort_index()
        # 267 takers and 3 needers
        # with no evidence in data of need solvable / unsolvable by $, assume solvable to be conservative
    df.loc[df['resp_len'].isna(), 'resp_len'] = 1
    # print(df.resp_len.isna().value_counts())

    # Pool of workers with 'length' not limited by replacement
    pool = df[(df['resp_len']==0) & (df.length>0)] # pool size = 262 workers
    # Workers with + response, current length known?
    # print(df[df['resp_len']==1].length.isna().value_counts()) # 1037 known, 170 missing

    return df, pool

# a function to get weighted mean using v-w columns
def get_wm_col(df, vws):
    num = pd.Series(np.zeros(len(df)))
    denom = pd.Series(np.zeros(len(df)))
    for v, w in vws:  # vws is list of var-weight tuples [('v0', 'w0'),...]
        num += df[v] * df[w]
        denom += df[w]
    return num / denom


# a function to fillna using knn
def fillna_knn(k, d0, d1, df, ixlabel, cols, v, w, vout):
    '''

    :param k: k in knn
    :param d0: df with v known
    :param d1: df with v missing
    :param df: master df used to fill in missing values in d0[cols] and d1[cols]
    :param ixlabel: label of index of d0, d1, and df for consistent merging
    :param cols: cols used to determine nearest neighbors
    :param v: label of variable to be filled in d0 and d1
    :param w: label of weight col in d0
    :param vout: label of weighted v col in d0 after fillna
    :return: d0 and d1 appended together, with v filled in
    '''

    locs0, locs1 = d0[cols], d1[cols]

    # fill in missing values
    for c in cols:
        locs0[c] = locs0[c].fillna(df[c].mean())
        locs1[c] = locs1[c].fillna(df[c].mean())
        # run kNN
    nbrs = NearestNeighbors(n_neighbors=k).fit(locs0)
    distances, indices = nbrs.kneighbors(locs1) # indices=order in locs0, not index of d0
        # translate indices from knn to index of d0 for merging
    Nnids = []
    for row in range(len(locs1)):
        nnids = []
        for kk in range(k):
            i = indices[row][kk]
            nnids.append(locs0[i:(i + 1)].index[0])  # these are the 2 kNNs (empid) identified
        Nnids.append(nnids)

        # make a df of nns for empids with missing current length
    dict_nn = dict(zip(locs1.index, Nnids))
    dnn = pd.DataFrame.from_dict(dict_nn, orient='index')
    dnn.index.rename(ixlabel, inplace=True)
    dnnCols = []
    for kk in range(k):
        dnnCols.append('nn%s' % kk)
    dnn.columns = dnnCols

        # use ixlabel of nns as key to merge with df[[ixlabel, v, w]]
    d1nn = df.join(dnn, how='right') # wkr dataset with nns, responsive, with length drawn from entire pool
    for kk in range(k):
        dfnn = df[[v, w]]
        dfnn['nn%s' % kk] = df.index
        dfnn.columns = ['resp%s' % kk, 'w%s' % kk, 'nn%s' % kk]
        d1nn = pd.merge(d1nn, dfnn, how='left', on='nn%s' % kk)

        # in resulting d1nn, compute weighted length using nns' empid
    vws = []
    for kk in range(k):
        vws += [('resp%s' % kk, 'w%s' % kk)]

    d1nn[vout] = get_wm_col(d1nn, vws)
    d1nn = d1nn.drop(columns=['nn%s' % kk for kk in range(k)] +
                                             [x[0] for x in vws] + [x[1] for x in vws])
                                            # x[0] picks resp<kk>, x[1] picks w<kk>

    # d01 = d0.append(d1nn)
    return d1nn

def get_resp_length(df, pool, params):
    # unpack knn parameters
    k, cols, ixlabel, v, w, vout = params

    # For workers with no response (interior solns), set resp_length = length
    wkrs_noResp = df[df['resp_len']==0]
    wkrs_noResp['resp_length'] = wkrs_noResp['length']
        # up to here, some interior-soln workers did not report length, they are EMPLOYED ONLY, no need
        # set resp_length = 0
    wkrs_noResp.loc[wkrs_noResp['LEAVE_CAT']==3, 'resp_length'] = 0

    # For responsive workers with known length, estimate length from pool of workers with greater length
    resp_wkrs = df[(df['resp_len']==1) & (df['length'].notna())]
    rwkrs_0nn = [] # list of resp wkrs with no nns, e.g. those with max leave length in entire sample
    wkrs_rnn_len = pd.DataFrame([])
    for row in range(len(resp_wkrs)):
        d1 = resp_wkrs[row:(row+1)] # pick a responsive worker
        wid = d1.index[0] # empid of responsive worker
        l = list(d1['length'])[0] # length of this worker's leave taken
        d0 = pool[pool['length'] > l] # eligible pool of nns are those with greater leave lengths
        if len(d0) >=k:
            # use kNN to estimate conditional length
            d1nn = fillna_knn(k, d0, d1, df, ixlabel, cols, v, w, vout)
            print('---- d1nn filled in for empid = %s, row %s-th done' % (wid, row))
            wkrs_rnn_len = wkrs_rnn_len.append(d1nn)
        else: # if not enough (less than k) leave takers with greater length in poolw
            rwkrs_0nn.append(wid)
            print('---->>> empid = %s has large leave length, insufficient eligible neighbors in pool, empid recorded to rwkrs_0nn' % wid)

    # For responsive workers with long length thus 0nn, get response using heuristics
    wkrs_r0nn_len = df.loc[rwkrs_0nn]
    wkrs_r0nn_len['resp_length'] = wkrs_r0nn_len['length'] * 1.5 # 1.5x for those w/o nns (long current length)

    # For responsive workers with missing length, draw length from entire pool
    d0 = pool
    d1 = df[(df['resp_len']==1) & (df['length'].isna())]
    wkrs_rnn_noLen = fillna_knn(k, d0, d1, df, ixlabel, cols, v, w, vout)

    # Append 4 resulting dfs:
    ds = [wkrs_noResp, wkrs_rnn_len, wkrs_r0nn_len, wkrs_rnn_noLen]
    dfr = pd.DataFrame([])
    for d in ds:
        dfr = dfr.append(d)


    return dfr

# a function to get parameters
def get_params():
    k = 2 # k of kNN
    cols = ['age',
            'male',
            'employed',
            'wkhours',
            'noHSdegree', 'BAplus',
            'empgov_fed', 'empgov_st', 'empgov_loc',
            'lnfaminc',
            'black', 'asian', 'hisp', 'other',
            'ndep_kid', 'ndep_old',
            'nevermarried', 'partner', 'widowed', 'divorced', 'separated']
    ixlabel = 'empid'
    v =  'length'
    w =  'freq_weight'
    vout = 'resp_length'
    params = (k, cols, ixlabel, v, w, vout)
    return params

# Get response
def get_response():
    df = pd.read_csv('./data/fmla_clean_2012.csv')
    df, pool = set_data(df) # Set data: df, pool
    params = get_params()
    dfr = get_resp_length(df, pool, params) # resulting df for all FMLA workers with response length generated
    dfr.to_csv('./data/fmla_clean_2012_resp_length.csv', index=False)
    return None

# get_response()

'''
# some checking
for d in ds:
    print(d.resp_length.isna().value_counts())

print('dfr length mean = \n', dfr.length.mean())
print('dfr resp_length mean = \n', dfr.resp_length.mean())
'''

