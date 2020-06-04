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

    def __init__(self, fileloader, reductionjob, filespecifier):
        """
        Initializes a Reduction instance
        
        Parameters
        ----------
        fileloader : subclass of(or) fileloader.FileLoaderBase
            FileLoaderBase or derived object to retrieve the required data of
            a '.tof' file as created by NICOS from a CASCADE detector's output.
        filespecifier : int
            integer value that specifies a certain ".tof" file for reduction
        reductionjob : ReductionJob
            A ReductionJob object that handles reduction of raw data arrays
            via reductionjob.run(selected_data)

        Return
        ------

        Notes
        -----
        """

        self.relevant_foils = fileloader.instrumentloader.get_Loader_settings("foils")
        self.filespecifier = filespecifier
        self.rawdata = None
        self.metadata = None
        self.reductionjob = reductionjob
        self.reductionjobresult = None

        self.get_data_from_file(fileloader)

#---------------------------------------------------------------------------------------------------

    def get_data_from_file(self, fileloader):
        """
        Retrieves Cascade data array and meta data from fileloader

        Parameters
        ----------
        fileloader : subclass of(or) fileloader.FileLoaderBase
            FileLoaderBase or derived object to retrieve the required data of
            a '.tof' file as created by NICOS from a CASCADE detector's output.

        Returns
        -------
        """
        fileloader.read_out_data(self.filespecifier)
        self.metadata = fileloader.datadict['metadata']

        self.rawdata = np.zeros((len(self.relevant_foils), 16, 128, 128))
        for idx, foilind in enumerate(self.relevant_foils):
            self.rawdata[idx] = fileloader.datadict['rawdata'][foilind]

#---------------------------------------------------------------------------------------------------

    def run(self):
        """
        Runs the reductionjob and saves result in self.reductionjobresult
        """
        self.reductionjobresult = self.reductionjob.run(self.rawdata)

##############################################################################
##############################################################################
##############################################################################

class ReductionStructure:
    """
    
    """
    def __init__(self, fileloader, *files, **kwargs):
        """
        
        """
        print("Instantiation will fail, not compatible with new `Redutction´ implementation!")
        self.fileloader = fileloader
        self.kwargs = kwargs
        if len(files) == 0:
            self.red_list = []
        else:
            self.red_list = [Reduction(self.fileloader, f) for f in files]
    
    def analyze(self, red_method, red_params, param_keys):
        """
        Run simple contrast calculation on all elements in self.red_list.
        Uses one rectangular area as mask.

        red_method : str
            chooses a reduction method in ["bootstrap", "simple_fit"]
        red_params ; dict
            will be passed to ``analyze´´ to specify reduction precedure
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

        # for redobj in self.red_list:
        #     if "lrbt" not in self.kwargs.keys():
        #         center = fit_beam_center(np.sum(np.sum(redobj.rawdata, axis=0), axis=0))
        #         lrbt = [int(center[1])-4 - 3, int(center[1])+5 - 3, int(center[0])-4, int(center[0])+5]
        #     else:
        #         lrbt = self.kwargs["lrbt"]


        #     redobj.prepare_fit_data(lrbt=lrbt)
        #     redobj.run_fits()
        #     tc = []
        #     tcerr = []
        #     for foil in redobj.relevant_foils:
        #         tc.append(redobj.fit_dict[foil]["contrast"])
        #         tcerr.append(redobj.fit_dict[foil]["contrast_err"])
        #     self.contrast.append(tc)
        #     self.contrast_err.append(tcerr)

        for redobj in self.red_list:
            redobj.run_reduction(job=red_method, **red_params)
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
        Quick plot option to visualize 'parameter' vs 'weighted_mean_contrast'

        Parameters
        ----------
        param_key       : str
            key to parameter in self.param_dict plotted on X axis
        param_name_str  : str
            name of parameter used for X axis label
        param_unit_str  : str
            unit of parameter used for X axis label
        legend_key      : str
            key to parameter of the plotted curve used in legend description
        legend_name_str : str
            name of parameter used in legend description
        ret             : bool
            True    --> returns fig, ax
            False   --> does not return fig, ax
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

    def to_file(self, fpath):
        nfoils = self.contrast.shape[1]
        nrows = len(self.weighted_mean_contrast)
        warr = np.empty((nrows, 2*nfoils + 2 + len(self.params_dict)))
        warr[:,-2-2*nfoils] = self.weighted_mean_contrast
        warr[:,-1-2*nfoils] = self.weighted_mean_contrast_err
        warr[:,-2*nfoils::2] = self.contrast
        warr[:,-2*nfoils+1::2] = self.contrast_err
        for idx, (pkey, params) in enumerate(self.params_dict.items()):
            if type(params) is not list:
                warr[:,idx] = nrows * [params]
            else:
                warr[:,idx] = params

        with open(fpath, "w") as wfile:
            contrast_descr = ["C weighted av.      , C weighted av. err  "] + [ ", ".join((f"{f'C foil {i+1}':20}", f"{f'C err foil {i+1}':20}")) for i in range(4)]
            param_descr = ", ".join([f"{f'### {key}':20}" if idx == 0 else f"{f'{key}':20}" for idx, key in enumerate(self.params_dict.keys())])
            wfile.write(param_descr + ", " + ", ".join(contrast_descr) + "\n")
            for slic in warr:
                wfile.write(", ".join([f"{f'{v:.15f}':20}" for v in slic]) + "\n")