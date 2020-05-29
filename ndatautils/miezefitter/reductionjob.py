import numpy as np

from abc import ABC, abstractmethod

###############################################################################
###############################################################################
###############################################################################

class ReductionJob(ABC):
    def __init__(self, selected_data, sinefitter):
        self.selected_data = selected_data
        self.sinefitter = sinefitter

    @abstractmethod
    def run(self):
        pass
    @staticmethod
    def prepare_fit_data(self, dataarray, lbwh=None, lrbt=None, pre_mask=None):
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
    def __init__(self, selected_data, sinefitter, **kwargs):
        super().__init__(selected_data, sinefitter)
        self.job_kwargs = {
            "lrbt" : None,
            "lbwh" : None,
            "pre_mask" : None
        }
        self.job_kwargs.update(kwargs)

#        if not any(job_kwargs.values()):
#            center = fit_beam_center(np.sum(np.sum(self.rawdata, axis=0), axis=0))
#            kwargs_dict["lrbt"] = [int(center[1])-4 - 3, int(center[1])+5 - 3, int(center[0])-4, int(center[0])+5]

    def run(self):
        sine_fit_result_list = []
        if any(self.job_kwargs.values()):
            for idx, (foilkey, dataarray) in enumerate(self.selected_data):
                temp_roi_counts = self.prepare_fit_data(dataarray, **self.job_kwargs)
                sine_fit_result_list.append( self.sinefitter.fit(np.arange(16), temp_roi_counts, temp_roi_counts**0.5) )

        else:
            raise ValueError("No ROI was propperly specified via **kwargs")

###############################################################################
###############################################################################
###############################################################################

class ReductionJobResult(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def populate(self):
        pass

###############################################################################

class AveragingReductionJobResult(ReductionJobResult):
    def __init__(self, *sinefitterresults):
        self.contrast = None
        self.contrast_err = None

        self.sinefitterresults = sinefitterresults

        self.populate()


    def populate(self):
        self.contrast = np.array([res.result_dict["contrast"] for res in self.sinefitterresults])
        self.contrast_err = np.array([res.result_dict["contrast_err"] for res in self.sinefitterresults])

        self.contrast = np.nansum(self.contrast * self.contrast_err**-2) / np.nansum(self.contrast_err**-2)
        self.contrast_err = np.nansum(self.contrast_err**-2)**-0.5
        