import numpy as np

from types import MethodType
from abc import ABC, abstractmethod
from numpy import pi
from lmfit import Model

from ..utils import sine, fit_beam_center

###############################################################################
###############################################################################
###############################################################################

def lmfit_backend_fitting(self, x, preped_data, weights):
    """
    Backend for fitting the sine function to the MIEZE signal

    Parameters
    ----------
    x : list, numpy.ndarray
        time bin indices
    preped_data : list, numpy.ndarray
        neutron counts of the MIEZE signal
    weights : list, numpy.ndarray
        weights associated with the neutron counts in each time bin

    Returns
    -------
    : SineFitResult
        results of the fit including contrast, contrast error
    """
    model = Model(sine)
            
    model.set_param_hint("A", min=0.0, value=(max(preped_data) - min(preped_data))/2.0)
    model.set_param_hint("omega", value=2*pi/16, vary=False)
    model.set_param_hint("phi", min=0.0, max=2*pi, value=((2 - np.argmax(preped_data) * 1/8 + 1/2)%2)*pi)
    model.set_param_hint("y0", min=0.0, value=np.mean(preped_data))

    weights = np.where(np.isnan(weights), np.zeros(len(weights)), weights)
    weights = np.where(np.isinf(weights), np.zeros(len(weights)), weights)

    backend_result = model.fit(x=x, data=preped_data, weights=weights)

    return SineFitResultlmfit(backend_result)

#------------------------------------------------------------------------------

def iminuit_backend_fitting():
    pass
    raise NotImplementedError
#    return SineFitResultiminuit(backend_result)

#------------------------------------------------------------------------------

class SineFitter:
    """
    An interface for fit algorithms based on different backends
    """
    def __init__(self, fitfunc=None):
        if fitfunc is not None:
            self.fit = MethodType(fitfunc, self)

    def fit(self):
        """
        Returns
        -------
        : SineFitResult or subclass
            Summarizes the fit results in a backend independent form
        """
        raise NotImplementedError

###############################################################################
###############################################################################
###############################################################################

class SineFitResult(ABC):
    """
    Base class of a standardized fit result object
    """
    def __init__(self, backend_result):
        self.resdict = {"contrast" : None,
                          "contrast_err" : None,
                          "phase" : None,
                          "phase_err" : None,
                          "chisqr" : None,
                          "redchi" : None,
                          "success" : None,
                          "raw_fit_vals" : {},
                          "raw_fit_errs" : {}
                          }
        self.populate(backend_result)

    def get(self, key):
        """
        Returns a value of the fit specified by 'key'

        Parameters
        ----------
        key : str
            key of a stored value

        Returns
        -------
        : None, float, dict
            value associated with 'key'
        """
        try:
            return self.resdict[key]
        except KeyError:
            raise KeyError(f"{key} is not a valid key. Only {self.resdict.keys()} are.")
    
    @abstractmethod
    def populate(self, backend_result):
        pass

#------------------------------------------------------------------------------

class SineFitResultlmfit(SineFitResult):
    """
    Summarizes values and parameters of a lmfit fit result object
    Contains values for the keys:
        'contrast'
        'contrast_err'
        'phase'
        'phase_err'
        'chisqr'
        'redchi'
        'success'
        'raw_fit_vals'
        'raw_fit_errs'
    """
    def populate(self, backend_result):
        self.resdict["contrast"] = backend_result.params["A"].value / backend_result.params["y0"].value
        try:
            self.resdict["contrast_err"] = self.resdict["contrast"] * np.sqrt((backend_result.params["A"].stderr/backend_result.params["A"].value)**2 + (backend_result.params["y0"].stderr/backend_result.params["y0"].value)**2)
        except TypeError:
            self.resdict["contrast_err"] = np.nan
        self.resdict["phase"] = backend_result.params["phi"].value
        self.resdict["phase_err"] = backend_result.params["phi"].stderr
        self.resdict["chisqr"] = backend_result.chisqr
        self.resdict["redchi"] = backend_result.redchi
        self.resdict["success"] = backend_result.success
        self.resdict["raw_fit_vals"] = {"A" : backend_result.params["A"].value,
                                           "omega" : backend_result.params["omega"].value,
                                           "phi" : backend_result.params["phi"].value,
                                           "y0" : backend_result.params["y0"].value
                                           }
        self.resdict["raw_fit_errs"] = {"A" : backend_result.params["A"].stderr,
                                           "omega" : backend_result.params["omega"].stderr,
                                           "phi" : backend_result.params["phi"].stderr,
                                           "y0" : backend_result.params["y0"].stderr
                                           }

#------------------------------------------------------------------------------

class SineFitResultiminuit(SineFitResult):
    def populate(self, backend_result):
        pass

###############################################################################
###############################################################################
###############################################################################