# -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the ndatautils contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Lukas Beddrich <lukas.beddrich@frm2.tum.de>
#
# *****************************************************************************

import numpy as np

from math import pi, sqrt
from lmfit import Model
import matplotlib.pyplot as plt

####################################################################################################
####################################################################################################
####################################################################################################

def gaussian_function(x, amp, x0, sig, bckg):
    """
    
    """

    return amp * 1.0/sqrt(2 * pi * sig * sig) * np.exp(- 0.5 * ((x - x0)/sig)**2) + bckg

#---------------------------------------------------------------------------------------------------

def sine(x, A, omega, phi, y0):
    """
    General sine function for fitting.
    
    Parameters
    ----------
    A     : float
        amplitude of the oscillation
    omega :
        angular frequency of the oscillation
    phi   :
        phase shift of the oscillation
    y0    :
        Intensity offset of the oscillation
    
    Return
    ------
    A * np.sin(omega * x + phi) + y0
    """
    
    return A * np.sin(omega * x + phi) + y0

#---------------------------------------------------------------------------------------------------

def fast_calc_beam_center(Ixy_data):
    """
    Calculates the center of a beam from a 2D dataset with I(x, y) as
    input. Simply weighting the array's index by the number of neutron
    counts acquired in the pixel.

    Parameters
    ----------
    Ixy_data: np.ndarray
        neutron intensity data as given by a 2D detector (CASCADE, 'neutron camera')

    Return
    ------
    ('center axis0', 'center axis1', 'center axis2', ...)

    Notes
    -----
    If the beam spot is close to the viewing field of the detector,
    such that part of the beam profile is cut off, this method gives
    less accurate results. Averaging underestimates the contribution
    cut of by detector boundary.

    Works also for n-dimensional data set I(x1, x2, ..., xn)
    """

    I_shape = Ixy_data.shape
    I_tot = Ixy_data.sum()

    def sum_axis(index, length):
        templist = list(range(length))
        templist.remove(index)
        return templist

    return tuple([np.sum(np.arange(l, dtype = float) * Ixy_data.sum(axis = tuple(sum_axis(i, len(I_shape)))) / I_tot) for i, l in enumerate(I_shape)])

#---------------------------------------------------------------------------------------------------

def fit_beam_center(Ixy_data):
    """
    Calculates the center of a 2D dataset with I(x, y) as
    input. Fitting a 1D gaussian function to each dimension summing
    over all remaining ones.

    Parameters
    ----------
    Ixy_data: np.ndarray
        neutron intensity data as given by a 2D detector (CASCADE, 'neutron camera')

    Return
    ------
    ('center axis0', 'center axis1', 'center axis2', ...)

    Notes
    -----
    works also for n-dimensional data set I(x1, x2, ..., xn)
    """

    def sum_axis(index, length):
        templist = list(range(length))
        templist.remove(index)
        return templist

    center_vals = []

    gaussian_model = Model(gaussian_function)
    gaussian_model.set_param_hint('amp', min=0)
    gaussian_model.set_param_hint('x0', min=0, max=128)
    gaussian_model.set_param_hint('sig', min=0)
    gaussian_model.set_param_hint('bckg', min=0)

    I_shape = Ixy_data.shape
    for i, l in enumerate(I_shape):
        fit_data = Ixy_data.sum(axis = tuple(sum_axis(i, len(I_shape))))
        x0_estimate = np.argmax(fit_data)
        temp_amp = np.max(fit_data)
        sig_estimate = len(np.where(fit_data > temp_amp/2)[0]) / 2.35
        amp_estimate = temp_amp * sqrt(2*pi) * sig_estimate
        fit_res = gaussian_model.fit(
                x=range(l),
                data=fit_data,
                amp=amp_estimate,
                x0=x0_estimate,
                sig=sig_estimate,
                bckg=0
                )
        center_vals.append(fit_res.params['x0'].value)

    return tuple(center_vals)

#---------------------------------------------------------------------------------------------------

def quickplotHistogram(histdata, bins=None, output=False):
    """
    Calculates the center of a beam from a 2D dataset with I(x, y) as
    input. Simply weighting the array's index by the number of neutron
    counts acquired in the pixel.

    Parameters
    ----------
    histdata: np.ndarray
        data for histogrammation
    bins: optional, np.ndarray, sequence
        defines bins and boundaries for the histograms data,
        otherwise bins the for min to max of histdata with
        #intervalls = #entries / 1000.
        else falls back to behaviour in np.histogram

    Return
    ------
    hist : array
        The values of the histogram. See `density` and `weights` for a
        description of the possible semantics.
    bin_edges : array of dtype float
        Return the bin edges ``(length(hist)+1)``


    """
    numentries = lambda arr: np.prod(arr.shape)
    if bins:
        hist, bin_edges = np.histogram(histdata, bins=bins)
    else:
        if numentires(histdata) / 1000 > 1:
            hist, bin_edges = np.histogram(histdata, bins=np.linspace(np.min(histdata), np.max(histdata), numentries(histdata) / 1000, endpoint=True))
        else:
            hist, bin_edges = np.histogram(histdata)
    
    x = [(b+bin_edges[i+1])/2 for i, b in enumerate(bin_edges[:-1])]
    width = [(bin_edges[i+1] - b) for i, b in enumerate(bin_edges[:-1])]
    plt.bar(x, hist, width=width, edgecolor="k", linewidth=1.0)
    plt.show()
    
    if output:
        return hist, bin_edges
        
        
    
