import numpy as np

from abc import ABC, abstractmethod

###############################################################################
###############################################################################
###############################################################################

class ReductionJob(ABC):
    """
    Base class for the ReductionJob interface
    """
    def __init__(self, sinefitter):
        self.sinefitter = sinefitter

    @abstractmethod
    def run(self, selected_data):
        pass

    @staticmethod
    def prepare_fit_data(dataarray, lbwh=None, lrbt=None, pre_mask=None):
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
        if (bool(lbwh), bool(lrbt), bool(pre_mask)) == (True, False, False):
            left, bottom, width, height = lbwh
            return np.sum(np.sum(dataarray[:,:,left:left+width], axis=-1)[:,bottom:bottom+height], axis=-1)
        elif (bool(lbwh), bool(lrbt), bool(pre_mask)) == (False, True, False):
            left, right, bottom, top = lrbt
            return np.sum(np.sum(dataarray[:,:,left:right], axis=-1)[:,bottom:top], axis=-1)
        elif (bool(lbwh), bool(lrbt), bool(pre_mask)) == (False, False, True):
            raise NotImplementedError
        else:
            raise ValueError("Preparation of fitting data failed. ROI specification required.")

###############################################################################

class ROIReductionJob(ReductionJob):
    """
    An implementation of the ReductionJob interface.
    The data is summed up in a predefined ROI before fitting the contrast
    """
    def __init__(self, sinefitter, job_kwargs={}, result_kwargs={}, **kwargs):
        """
        Parameters
        ----------
        sinefitter : ..sinefitter.SineFitter
            A SineFitter instance that provides an interface to a selected
            fitting backend (lmfit, iminuit)
        job_kwargs : dict
            specifies the used ROI format as key and the ROI itself
        result_kwargs : dict
            specifies the format of the ReductionJobResult, which is
            instantiated by the factory
        
        Returns
        -------
        ROIReductionJob implementation
        """
        super().__init__(sinefitter)
        self.job_kwargs = {
            "lrbt" : None,
            "lbwh" : None,
            "pre_mask" : None
        }
        self.result_kwargs = {
            "key" : "allaverage"
        }
        self.job_kwargs.update(job_kwargs)
        self.result_kwargs.update(result_kwargs)

#        if not any(job_kwargs.values()):
#            center = fit_beam_center(np.sum(np.sum(self.rawdata, axis=0), axis=0))
#            kwargs_dict["lrbt"] = [int(center[1])-4 - 3, int(center[1])+5 - 3, int(center[0])-4, int(center[0])+5]

    def run(self, selected_data):
        """
        Runs the ROI contraction on the 2D detector data array and
        fits the retrieved sine signal

        Parameters
        ----------
        selected_data : numpy.ndarray
            2D Cascade detecor data
            shape: (x, 16, 128, 128)

        Returns
        -------
            : subclass of ReductionJobResult
            Result of the contrast extraaction
        """
        sine_fit_result_list = []
        if any(self.job_kwargs.values()):
            for dataarray in selected_data:
                temp_roi_counts = self.prepare_fit_data(dataarray, **self.job_kwargs)
                sine_fit_result_list.append( self.sinefitter.fit(np.arange(16), temp_roi_counts, temp_roi_counts**0.5) )
            return result_factory.create(*sine_fit_result_list, **self.result_kwargs)

        else:
            raise ValueError("No ROI was propperly specified via **kwargs")

#------------------------------------------------------------------------------

class MultiROIReductionJob(ReductionJob):
    def __init__(self, sinefitter, **kwargs):
        super().__init__(sinefitter)
        self.job_kwargs = {
            "lrbt" : None,
            "lbwh" : None,
            "pre_mask" : None
        }
        self.job_kwargs.update(kwargs)

    def run(self, selected_data):
        raise NotImplementedError("This has not been properly implemented yet!")
        sine_fit_result_list = []
        if any(self.job_kwargs.values()):
            for idx, dataarray in enumerate(selected_data):
                temp_roi_counts = self.prepare_fit_data(dataarray, **self.select_kwargs(idx))
                sine_fit_result_list.append( self.sinefitter.fit(np.arange(16), temp_roi_counts, temp_roi_counts**0.5) )
            return AveragingReductionJobResult(*sine_fit_result_list)

        else:
            raise ValueError("No set of ROIs was propperly specified via **kwargs")

    def select_kwargs(self, idx):
        temp_job_kwargs = {
            "lrbt" : None,
            "lbwh" : None,
            "pre_mask" : None
        }
        for key, roi in self.job_kwargs.items():
            if roi:
                temp_job_kwargs[key] = roi[idx]
                return temp_job_kwargs

###############################################################################
###############################################################################
###############################################################################

class ReductionJobResult(ABC):
    """
    Base class for the ReductionJobResult interface
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def populate(self):
        pass

###############################################################################

class AveragingReductionJobResult(ReductionJobResult):
    """
    Instance of a ReductionJobResult subclass that stores
    a weighted average and its error of the contrast over all
    sinefitterresults (basically over all foils)
    """
    def __init__(self, *sinefitterresults, **_ignored):
        """
        Parameters
        ----------
        *sinefitterresults : ..sinefitter.SineFitterResult
            arbitrary number of intermediate SineFitterResult objects
            to be processed into the final result
        **_ignored : dict
            any number of additional kwargs which are ignored
        """
        self.contrast = None
        self.contrast_err = None

        self.sinefitterresults = sinefitterresults

        self.populate()


    def populate(self):
        self.contrast = np.array([res.resdict["contrast"] for res in self.sinefitterresults])
        self.contrast_err = np.array([res.resdict["contrast_err"] for res in self.sinefitterresults])

        self.contrast = np.nansum(self.contrast * self.contrast_err**-2) / np.nansum(self.contrast_err**-2)
        self.contrast_err = np.nansum(self.contrast_err**-2)**-0.5

#------------------------------------------------------------------------------

class SelctedFoilAveragingReductionJobResult(ReductionJobResult):
    """
    Instance of a ReductionJobResult subclass that stores
    a weighted average and its error of the contrast over a selection of
    sinefitterresults
    """
    def __init__(self, *sinefitterresults, **kwargs):
        """
        Parameters
        ----------
        *sinefitterresults : ..sinefitter.SineFitterResult
            arbitrary number of intermediate SineFitterResult objects
            to be processed into the final result
        **kwargs : dict
            'foilsdix' : list with viable indices for averaging
        """
        self.contrast = None
        self.contrast_err = None

        self.sinefitterresults = sinefitterresults

        self.populate(kwargs['foilsidx'])

    def populate(self, foilsidx):
        self.contrast = np.array([res.resdict["contrast"] for res in self.sinefitterresults])
        self.contrast_err = np.array([res.resdict["contrast_err"] for res in self.sinefitterresults])

        self.contrast = np.nansum(self.contrast[foilsidx] * self.contrast_err[foilsidx]**-2) / np.nansum(self.contrast_err[foilsidx]**-2)
        self.contrast_err = np.nansum(self.contrast_err[foilsidx]**-2)**-0.5

#------------------------------------------------------------------------------

class SelectedFoilReductionJobResult(ReductionJobResult):
    """
    Instance of a ReductionJobResult subclass that stores
    a the contrast and its error of a selected sinefitterresult
    """
    def __init__(self, *sinefitterresults, **kwargs):
        """
        Parameters
        ----------
        *sinefitterresults : ..sinefitter.SineFitterResult
            arbitrary number of intermediate SineFitterResult objects
            to be processed into the final result
        **kwargs : dict
            'idx' : index of the chosen SineFitterResult
        """
        self.contrast = None
        self.contrast_err = None

        self.sinefitterresults = sinefitterresults

        self.populate(kwargs['idx'])

    def populate(self, idx):
        self.contrast = self.sinefitterresults[idx].resdict["contrast"]
        self.contrast_err = self.sinefitterresults[idx].resdict["contrast_err"]


###############################################################################
###############################################################################
###############################################################################

class ReductionJobResultFactory:
    """
    Factory class for subclass instances of ReductionJobResult
    Registers any available ReductionJobResult by key for creation
    """
    def __init__(self):
        self._result_format_register = {}
    def add_result_format(self, key, result_format):
        self._result_format_register[key] = result_format
    def create(self, *args, **kwargs):
        creator = self._result_format_register.get(kwargs["key"])
        if not creator:
            raise ValueError(f"{kwargs['key']} is not linked to a valid creator")
        return creator(*args, **kwargs)

result_factory = ReductionJobResultFactory()
result_factory.add_result_format("allaverage", AveragingReductionJobResult)
result_factory.add_result_format("selectiveaverage", SelctedFoilAveragingReductionJobResult)
result_factory.add_result_format("selectfoil", SelectedFoilReductionJobResult)