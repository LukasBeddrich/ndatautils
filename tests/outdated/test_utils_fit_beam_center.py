""" Script to test the 'fit_beam_center' method"""
import matplotlib.pyplot as plt
import numpy as np
import os

from lmfit import Model
from pprint import pprint
from sys import path
from scipy.stats import multivariate_normal
#-----------------------------------------------------------------------
from ndatautils.utils import gaussian_function, fast_calc_beam_center, fit_beam_center
########################################################################
# Loading test data from utils_fit_beam_center.npz archive

DataNpzFile = np.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata/utils_fit_beam_center.npz"))
print(DataNpzFile.files)

#-----------------------------------------------------------------------
# Check functionality of ndatautils.utils.fit_beam_center
supposed_center = {
        '146695' : (62, 66),
        '146696' : (9, 66),
        '147505' : (1, 70),
        '147508' : (2, 68),
        '147509' : (4, 67),
        '147510' : (4, 67),
        '147511' : (4, 67),
        '147513' : (1, 70),
        }

for key, item in supposed_center.items():
    print("File {}, supposed center of beam:  ".format(key), item)
    temp_center = fit_beam_center(DataNpzFile[str(key)])
    print("File {}, calculated center of beam: ({:.0f}, {:.0f})".format(
            key, temp_center[1], temp_center[0]
            ))

