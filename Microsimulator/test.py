from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from Settings import Settings
from test2 import editSettings
from sklearn import linear_model
from StaticObj import StaticObj, increment

#
# df = pd.read_csv("test.csv")
# values = list(df['PUMA00'])
# serial = list(df['SERIALNO'])
# soc = list(df['SOCP12'])
# print(values[0], type(values[0]))
# print(serial[0], type(serial[0]))
# print(soc[0], type(soc[0]))
#
# target = df[df['SERIALNO'] == 2011000000097]
# target2 = df[df.PUMA00 == 100]
# print(target)
# print(target2)

# ocp10 = list(df['SOCP10'])
# print(len(serial))
# print(ocp10[47])
# print(int(''.join(c for c in ocp10[47] if c.isdigit())))

# for i, row in df.iterrows():
#     print(list(row))

# X = np.matrix([2, 3, 1]).reshape((3, 1))
# X = np.column_stack((X, np.ones(3)))
# y = np.matrix([1, 1, -1]).reshape((3, 1))
# print(X)
# print(X.T)
# print(np.dot(X.T, X))
# print(np.linalg.pinv(np.dot(X.T, X)))
# print(np.dot(np.linalg.pinv(np.dot(X.T, X)), np.dot(X.T, y)))
#
# reg = linear_model.LinearRegression()
# reg.fit([[2], [3], [1]], [1, 1, -1])
# print(reg.coef_, reg.intercept_)

# print(StaticObj.val)
# increment()
# print(StaticObj.val)
# StaticObj.val = 'asd'
# print(StaticObj.val)
# editSettings()
# print(StaticObj.val)

df = pd.read_csv('parameters/length ILL CHILD men 2.txt', sep='\t')
df.columns = ['num', 'prob']
print(df)
