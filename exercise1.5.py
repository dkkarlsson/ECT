#exercise 5

import numpy as np
import scipy
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import operator
from strfuncs import *
import re
np.set_printoptions(threshold = sys.maxsize)
pd.options.display.max_rows = sys.maxsize

def read_AME(filename):
    formfile = open(filename, 'r').read()
    start = 'format    :'
    formats = formfile[find_nth(formfile, start, 1)+len(start):find_nth(formfile, 'Warnings', 1)].split('\n')
    widths = [int(re.findall('[0-9]+', x)[0]) for x in formats[0].strip().split(',')]
    names = formfile.split('\n')[37].replace('BINDING ENERGY/A','BE/A dBE/A').replace('MASS EXCESS','dM ddM').replace('BETA-DECAY ENERGY','Type E dE').replace('ATOMIC MASS','u du').split()[1:]
    infile = open('mass16.txt', 'r')
    Masses = pd.read_fwf(infile, widths = widths, names = [i for i in range(len(widths))], header = 39)
    #print([x for x in Masses[5].values if not np.isnan(x)])
    Masses[18] = [x.replace('.','') for x in Masses[18].astype(str)]
    Masses[20] = [x.replace('.','') for x in Masses[20].astype(str)]
    Masses[18] = Masses[[18,20]].apply('.'.join, axis = 1)
    Masses = Masses.drop([0,1,5,8,13,17,19,20], axis = 1)
    Masses.columns = names
    Masses.index = Masses['Z'].astype(str) + '-' + Masses['N'].astype(str)
    return Masses

df = read_AME('mass16.txt')

#print(Masses[-20:])
print(df)


