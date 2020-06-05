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
    def __init__(self, *reductions, **kwargs):
        """
        Constructor with Reduction objects
        """
        self.contrast = None
        self.contrast_err = None
        self.params_dict = None
        self.kwargs = kwargs
        if len(reductions) == 0:
            self.red_list = []
        else:
            self.red_list = list(reductions)

#------------------------------------------------------------------------------

    @classmethod
    def from_tuple(cls, *components, **kwargs):
        """
        Alternate constructor from a tuple of Reduction components

        Parameters
        ----------
        *components : tuple(s)
            each compnents tuple needs:
            - fileloader derived from ndatautils.fileloader.FileLoaderBase
            - reductionjob derived from ndatautils.miezefitter.reductionjob.ReductionJob
            - filespecifier integer value of the file
        """
        return cls(*[Reduction(fileloader, reductionjob, filespecifier) for fileloader, reductionjob, filespecifier in components], **kwargs)

#------------------------------------------------------------------------------
    
    def analyze(self, param_keys):
        """
        Runs contrast extraction on all elements in self.red_list
        via their ReductionJob instance.
        Simultaneously, retrieves specified measurement parameters
        from each object in self.red_list

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

        param_keys.update({"echotime_value" : "tau_M"}) # Standard add MIEZE time
        self.params_dict = self.get_params(**param_keys)

        for redobj in self.red_list:
            redobj.run()
            self.contrast.append(redobj.reductionjobresult.contrast)
            self.contrast_err.append(redobj.reductionjobresult.contrast_err)

    def get_results(self):
        return self.contrast, self.contrast_err, self.params_dict

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
        seldict = {}
        for redobj in self.red_list:
            metadata = redobj.metadata
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
        nrows = len(self.contrast)
        warr = np.empty((nrows, 2 + len(self.params_dict)))
        warr[:,-2] = self.contrast
        warr[:,-1] = self.contrast_err
        for idx, params in enumerate(self.params_dict.values()):
            if type(params) is not list:
                warr[:,idx] = nrows * [params]
            else:
                warr[:,idx] = params

        with open(fpath, "w") as wfile:
            contrast_descr = ["Contrast            , Contrast Error      "]
            param_descr = ", ".join([f"{f'### {key}':20}" if idx == 0 else f"{f'{key}':20}" for idx, key in enumerate(self.params_dict.keys())])
            wfile.write(param_descr + ", " + ", ".join(contrast_descr) + "\n")
            for slic in warr:
                wfile.write(", ".join([f"{f'{v:.15f}':20}" for v in slic]) + "\n")

    def plot(self, legend_key, legend_name_str, legend_unit_str, param_key='tau_M', param_name_str='$\\tau_\\mathrm{M}$', param_unit_str='ns', ret=False):
        """
        Quick plot option to visualize 'parameter' vs 'contrast'

        Parameters
        ----------
        legend_key      : str
            key to parameter of the plotted curve used in legend description
        legend_name_str : str
            name of parameter used in legend description
        legend_unit_str  : str
            unit of parameter used in legend description
        param_key       : str
            key to parameter in self.param_dict plotted on X axis
        param_name_str  : str
            name of parameter used for X axis label
        param_unit_str  : str
            unit of parameter used for X axis label
        ret             : bool
            True    --> returns fig, ax
            False   --> does not return fig, ax
        """
        fig, ax = plt.subplots(figsize=(7.5,5), dpi=200)
        ax.errorbar(self.params_dict[param_key],
                    self.contrast,
                    self.contrast_err,
                    mew=2.0, ls="", marker="s", mfc="w", mec="C0", ms=7, capsize=5, ecolor="C0",
                    label=f"{legend_name_str} = {self.params_dict[legend_key]} [{legend_unit_str}]",
                   )

        ax.tick_params("both", labelsize=16)
        ax.set_xlabel(f"{param_name_str} in [{param_unit_str}]", fontsize=18) # r"$\tau_\mathrm{MIEZE}$ in [ns]"
        ax.set_ylabel("Contrast in [arb. u.]", fontsize=18)
        ax.legend(loc="best", fontsize=13, markerscale=0.9)
        if ret:
            return fig, ax