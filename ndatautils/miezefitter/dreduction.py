# -*- coding: utf-8 -*-

### Imports
import numpy as np
import matplotlib.pyplot as plt
from ..utils import sine, fit_beam_center
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

#-----------------------------------------------------------------------------

def check_red_fit(redobj, lrbt, foil=0, ret=False):
    """
    visualizes the fit of a reduction instance

    Parameters
    ----------
    redobj : ndatautils.miezefitter.Reduction
        
    lrbt   : tuple, list
        lrbt : [left, right, bottom, top], None
        integer values in 128x128 to specify ROI
    foil   : int
        integer from 0 to 7 selects foil of Cascade dataset
    ret    : bool
        specifies if figure und axes of the plot are returned

    Returns
    -------
    fix, ax : matplotlib.figure.Figure, matplotlib.axis._subplots.AxesSubplot
        used figure and axis instance
    """
    redobj.prepare_fit_data(lrbt=lrbt)
    result = redobj.single_fit(np.arange(0,16), redobj.preped_data[foil], np.sqrt(redobj.preped_data[foil])**-1)
    params = [result["raw_fit_vals"][key] for key in ["A", "omega", "phi", "y0"]]

    fig, ax = plt.subplots(figsize=(7.5,5))
    ax.errorbar(np.arange(0,16), redobj.preped_data[foil], np.sqrt(redobj.preped_data[foil]), ls="", marker="o", ms=7, color="C0", capsize=5,
                label="C: {:.2f} $\pm$ {:.2f}".format(result["contrast"], result["contrast_err"]))
    ax.plot(np.linspace(0,15,101), sine(np.linspace(0,15,101), *params), color="C0", label="fit")
    ax.tick_params("both", labelsize=16)
    ax.set_xlabel(r"time bins", fontsize=18)
    ax.set_ylabel(r"Counts in 10$\,$s", fontsize=18)
#    ax.set_ylim(ymin=0, ymax=0.56)
#    ax.set_xlim((0.0, 0.35))
    ax.legend(loc="upper center", fontsize=13, markerscale=0.75)

    if ret:
        return fig, ax

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

##############################################################################
##############################################################################
##############################################################################

class ReductionStructure:
    """
    
    """
    def __init__(self, fileloader, *files, **kwargs):
        """
        
        """
        self.fileloader = fileloader
        self.kwargs = kwargs
        if len(files) == 0:
            self.red_list = []
        else:
            self.red_list = [Reduction(self.fileloader, f) for f in files]
    
    def analyze(self, **param_keys):
        """
        Run simple contrast calculation on all elements in self.red_list.
        Uses one rectangular area as mask.

        param_keys : dict
            general sturcture is {'metadata_key' : 'alias', ...} where the
            'metadata_key' specifies an entry in the
            self.fileloader.datadict["metadata"]["main_key"]
            'alias' is the key for sef.params_dict

        Examples
        --------
        >>> example_structure = ReductionStructure(...)
        >>> example_structure.analyze(dtx_value="theta_D"})
        """
        self.contrast = []
        self.contrast_err = []

        param_keys.update(dict([("echotime_value", "tau_M")])) # Standard add MIEZE time
        self.params_dict = self.get_params(**param_keys)

        for redobj in self.red_list:
            center = fit_beam_center(np.sum(np.sum(redobj.rawdata, axis=0), axis=0))
            lrbt = [int(center[1])-4 - 3, int(center[1])+5 - 3, int(center[0])-4, int(center[0])+5]


            redobj.prepare_fit_data(lrbt=lrbt)
            redobj.run_fits()
            tc = []
            tcerr = []
            for foil in redobj.relevant_foils:
                tc.append(redobj.fit_dict[foil]["contrast"])
                tcerr.append(redobj.fit_dict[foil]["contrast_err"])
            self.contrast.append(tc)
            self.contrast_err.append(tcerr)

        self.contrast = np.array(self.contrast)
        self.contrast_err = np.array(self.contrast_err)
        self.weighted_mean_contrast = np.nansum(self.contrast[:,(0,2,3)]*self.contrast_err[:,(0,2,3)]**-2, axis=1)/np.nansum(self.contrast_err[:,(0,2,3)]**-2, axis=1)
        self.weighted_mean_contrast_err = np.sqrt(1 / np.nansum(self.contrast_err[:,(0,2,3)]**-2, axis=1))

    def get_results(self):
        return self.contrast, self.contrast_err, self.params_dict

    def plot(self, param_key, param_name_str, param_unit_str, legend_key, legend_name_str, ret=False):
        """

        """
        fig, ax = plt.subplots(figsize=(7.5,5), dpi=300)
        ax.errorbar(self.params_dict[param_key],
                    self.weighted_mean_contrast,
                    self.weighted_mean_contrast_err,
                    mew=2.0, ls="", marker="s", mfc="w", mec="C0", ms=7, capsize=5, ecolor="C0",
                    label=r"{} = {}".format(legend_name_str, self.params_dict[legend_key]),
                   )

        ax.tick_params("both", labelsize=16)
        ax.set_xlabel(r"{} in [{}]".format(param_name_str, param_unit_str), fontsize=18) # r"$\tau_\mathrm{MIEZE}$ in [ns]"
        ax.set_ylabel(r"Contrast in [arb. u.]", fontsize=18)
        legend = ax.legend(loc="best", fontsize=13, markerscale=0.9)
        if ret:
            return fig, ax

    def get_params(self, **param_keys):
        """
        Returns the metadata specified by keys. Can be either 'mainkey' or 'subkey'.
        Returns the entire dictionary if no key is given.
        --------------------------------------------------

        Arguments:
        ---------- 
        *keys       : list  : list of keys for metadata retrieval

        Returns:
        ----------
        seldict     : dict  : dictionary containing metadata {'mainkey' : subdict, 'subkey' : item ,...}
        """

        self.fileloader.instrumentloader.set_Loader_settings(rawdata=False)
        seldict = {}
        for redobj in self.red_list:
            self.fileloader.read_out_data(redobj.filespecifier)
            metadata = self.fileloader.datadict["metadata"]
            for key, alias in param_keys.items():
                for subdict in metadata.values():
                    if key in subdict.keys() and alias in seldict.keys():
                        if isinstance(subdict[key][0], float):
                            seldict[alias].append(subdict[key][0])
                        else:
                            seldict[alias].append(0)
                    elif key in subdict.keys():
                        if isinstance(subdict[key][0], float):
                            seldict[alias] = [subdict[key][0]]
                        else:
                            seldict[alias] = [0]
        for k, vs in seldict.items():
            if np.isclose(max(vs), min(vs)):
                seldict[k] = max(vs)

        return seldict