# -*- coding: utf-8 -*-

### Imports
import numpy as np
from ..utils import sine
from numpy import pi
from lmfit import Model
###

def create_model(func, backend="lmfit"):
    """
    Returns a model-class of the selected package for fitting.

    Parameters
    ----------
    func    : 
        sth

    backend : str
        - lmfit: uses `lmfit´ package for fitting
        - iminuit: uses `iminuit´ package for fitting

    Return
    ------
    model   : lmfit.Model or iminuit.Minuit object
    """
    if backend.upper() == "LMFIT":
        model = Model(func)
        model.set_param_hint("A", min=0.0)
        model.set_param_hint("omega", value=2*pi/16, vary=False)
        model.set_param_hint("phi", min=0.0, max=2*pi)
        model.set_param_hint("y0", min=0.0)
        return model

    elif backend.upper() == "IMINUIT":
        raise NotImplementedError

    else:
        raise KeyError("The backend '{}' is not recognized.".format(backend))

####################################################################################################
####################################################################################################
####################################################################################################

class Reduction:
    """
    
    """

    def __init__(self, fileloader, filespecifier, backend="lmfit"):
        """
        Initializes a Reduction instance
        
        Parameters
        ----------
        fileloader : subclass of(or) fileloader.FileLoaderBase
            FileLoaderBase or derived object to retrieve the required data of
            a '.tof' file as created by NICOS from a CASCADE detector's output.
        filespecifier : int
            integer value that specifies a certain ".tof" file for reduction
        backend : str
            - lmfit: uses `lmfit´ package for fitting
            - iminuit: uses `iminuit´ package for fitting

        instrumentloader : subclass of(or) instrumentloader.InstrumentLoader
            Contains the information of the instrument of the used in the experiment.

        Return
        ------

        Notes
        -----
        """

        self.fileloader = fileloader
        self.filespecifier = filespecifier
        self.instrumentloader = fileloader.instrumentloader
        self.relevant_foils = self.instrumentloader.get_Loader_settings("foils")
        self.backend = backend
        self.rawdata = None
        self.preped_data = None
        self.fit_dict = None
        
        self.get_data_from_file()
        self.create_model()

#---------------------------------------------------------------------------------------------------

    def get_data_from_file(self):
        """
        
        """
        self.fileloader.read_out_data(self.filespecifier)
        self.rawdata = np.zeros((len(self.relevant_foils), 16, 128, 128))
        for idx, foilind in enumerate(self.relevant_foils):
            self.rawdata[idx] = self.fileloader.datadict['rawdata'][foilind]

#---------------------------------------------------------------------------------------------------

    def create_model(self):
        """
        Creates a lmfit.Model or iminuit.Minuit object to fit the MIEZE signal.

        Parameters
        ----------
        self.backend : str
            - lmfit: uses `lmfit´ package for fitting
            - iminuit: uses `iminuit´ package for fitting

        Notes
        -----
        Only `lmfit´ works as a backend for fitting.
        """
        self.model = create_model(sine, self.backend)

#---------------------------------------------------------------------------------------------------
#
#    def set_model_params(self):
#        """
#
#        """
#
#---------------------------------------------------------------------------------------------------

    def prepare_fit_data(self, lbwh=None, lrbt=None, pre_mask=None):
        """
        Prepare the raw data for fit by summing counts in ROI.
        Populates self.preped_data

        Parameters
        ----------
        lbwh : [left, bottom, width, height], None
            integer values in 128x128 to specify ROI
        lrbt : [left, right, bottom, top], None
            integer values in 128x128 to specify ROI
        pre_mask : pre_mask object or numpy.ndarray
            mask/mask-array that specifies a ROI
        """
        self.preped_data = np.zeros(self.rawdata.shape[:2])
        if (bool(lbwh), bool(lrbt), bool(pre_mask)) == (True, False, False):
            left, bottom, width, height = lbwh
            self.preped_data = np.sum(np.sum(self.rawdata[:,:,:,left:left+width], axis=-1)[:,:,bottom:bottom+height], axis=-1)
        elif (bool(lbwh), bool(lrbt), bool(pre_mask)) == (False, True, False):
            left, right, bottom, top = lrbt
            self.preped_data = np.sum(np.sum(self.rawdata[:,:,:,left:right], axis=-1)[:,:,bottom:top], axis=-1)
        elif (bool(lbwh), bool(lrbt), bool(pre_mask)) == (False, False, True):
            raise NotImplementedError
        else:
            raise ValueError("Preparation of fitting data failed. ROI specification required.")

#---------------------------------------------------------------------------------------------------

    def single_fit(self, x, preped_data, weights, full_fit_res=False):
        """
        Fits a sine curve into a prepared data set.
        
        Parameters
        ----------
        x : numpy.ndarray
            x-coordinate value
        prepared_data : numpy.ndarray
            one period of the time modulated neutron intensity
        weights : numpy.ndarray
            weights for the residuals in the chi square fit

        Return
        ------
        result_dict : dict
            summarized information of the fit
        """
        result_dict = {}
        if self.backend.upper() == "LMFIT":
            
            self.model.set_param_hint("A", min=0.0, value=(max(preped_data) - min(preped_data))/2.0)
            self.model.set_param_hint("omega", value=2*pi/16, vary=False)
            self.model.set_param_hint("phi", min=0.0, max=2*pi, value=((2 - np.argmax(preped_data) * 1/8 + 1/2)%2)*pi)
            self.model.set_param_hint("y0", min=0.0, value=np.mean(preped_data))
            
            sfit_res = self.model.fit(x=x, data=preped_data, weights=weights)
            
            if full_fit_res: # Abbort if I detect a problem with calculating contrast or its error
                return sfit_res

            result_dict["contrast"] = sfit_res.params["A"].value / sfit_res.params["y0"].value
            try:
                result_dict["contrast_err"] = result_dict["contrast"] * np.sqrt((sfit_res.params["A"].stderr/sfit_res.params["A"].value)**2 + (sfit_res.params["y0"].stderr/sfit_res.params["y0"].value)**2)
            except TypeError:
                result_dict["contrast_err"] = np.nan
            result_dict["phase"] = sfit_res.params["phi"].value
            result_dict["phase_err"] = sfit_res.params["phi"].stderr
            result_dict["chisqr"] = sfit_res.chisqr
            result_dict["redchi"] = sfit_res.redchi
            result_dict["success"] = sfit_res.success
            result_dict["raw_fit_vals"] = {"A" : sfit_res.params["A"].value,
                                           "omega" : sfit_res.params["omega"].value,
                                           "phi" : sfit_res.params["phi"].value,
                                           "y0" : sfit_res.params["y0"].value
                                           }
            
        elif self.backend.lower() == "iminuit":
            raise NotImplementedError

        return result_dict

#---------------------------------------------------------------------------------------------------

    def run_job(self, job):
        """
        Starts fitting of the data, according to a specified 'job'

        Parameters
        ----------
        job : str
            specifies what to do

        Return
        ------
        """
        if job.lower() == "individual_fitting":
            self.run_fits()
        elif job.lower() == "superimposed_fitting":
            raise NotImplementedError
        else:
            raise KeyError("The execution of the requested job failed. Job specifier not known.")


#---------------------------------------------------------------------------------------------------

    def run_fits(self):
        """
        
        """
        self.fit_dict = {}
        for idx, foilind in enumerate(self.relevant_foils):
            self.fit_dict[foilind] = self.single_fit(list(range(16)), self.preped_data[idx], np.sqrt(self.preped_data[idx])**-1)

#---------------------------------------------------------------------------------------------------