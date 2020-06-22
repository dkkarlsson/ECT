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
import operator

def pol2(x, A, B, C):
    return A + B*x + C*x**2

def MSE(yexp, ymod):
    return 1/len(yexp)*np.sum((yexp-ymod)**2)

def R2(yexp, ymod):
    return 1 - (np.sum((yexp-ymod)**2))/(np.sum((yexp - np.mean(yexp))**2))

def RelativeError(yexp, ymod):
    return abs((yexp - ymod)/yexp)

x = np.random.rand(100,1)
y = 5*x**2 +0.2*np.random.randn(100,1)
linreg = LinearRegression()
linreg.fit(x,y)
xnew = np.array([[0],[1]])
ypredict = linreg.predict(xnew)
#plt.plot(xnew, ypredict)
plt.scatter(x,y, c = 'r')

p = 3
A = np.zeros((len(x), p))
for i in range(p):
    A[:,i] = x.T**i
X = pd.DataFrame(A)
X.columns = ['1', 'x', 'x**2']

beta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

ytilde = X @ beta

x, ytilde = zip(*sorted(zip(x, ytilde.values), key = operator.itemgetter(0)))

plt.plot(x, ytilde, c = 'k')
plt.show()
plt.clf()
sys.exit()





