import numpy as np
import scipy
import keras
#import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
#import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import operator

def pol2(x, A, B, C):
    return A + B*x + C*x**2

def MSE(yexp, ymod):
    return 1/len(yexp)*np.sum((yexp-ymod)**2)

def R2(yexp, ymod):
    return 1 - np.sum((yexp-ymod)**2)/np.sum((yexp - np.mean(yexp))**2)

def RelativeError(yexp, ymod):
    return abs((yexp - ymod)/yexp)

x = np.random.rand(100,1)
y = 5*x**2 +0.8*np.random.randn(100,1)
poly2 = PolynomialFeatures(degree = 2)
plt.scatter(x,y, c='r')
x2 = poly2.fit_transform(np.ndarray.flatten(x)[:,np.newaxis])
 
linreg = LinearRegression()
linreg.fit(x2,y)

Xplot = poly2.fit_transform(np.ndarray.flatten(x)[:,np.newaxis])
ypredict = linreg.predict(Xplot)
x2, ypredict = zip(*sorted(zip(x, ypredict), key = operator.itemgetter(0)))
plt.plot(x2, ypredict, c = 'b', linestyle = '--',lw = 3)

p = 3
A = np.zeros((len(x), p))
for i in range(p):
    A[:,i] = x.T**i
X = pd.DataFrame(A)
X.columns = ['1', 'x', 'x**2']

beta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

ytilde = X @ beta

x, ytilde = zip(*sorted(zip(x, ytilde.values), key = operator.itemgetter(0)))

plt.plot(x, ytilde, c = 'g',linestyle = '-.', lw = 2)
plt.show()
plt.clf()

print(MSE(y,ypredict))
print(R2(y,ypredict))
print(MSE(y,ytilde))
print(R2(y,ytilde))
print(mean_squared_error(y,ypredict))
print(r2_score(y,ypredict))
print(mean_squared_error(y,ytilde))
print(r2_score(y,ytilde))




