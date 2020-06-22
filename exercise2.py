import numpy as np
import scipy
import keras
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

df = pd.read_csv('EoS.csv', names = ['0', '1'])
p = 4
A = np.zeros((len(df['0'].values), p))
for i in range(p):
    A[:,i] = df['0']**i
designMatrix = pd.DataFrame(A)
designMatrix.columns = ['1', 'x', 'x**2', 'x**3']
print(designMatrix)

