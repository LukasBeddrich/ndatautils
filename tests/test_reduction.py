import numpy as np
import pytest
#------------------------------------------------------------------------------
from ndatautils.datapath import CustomDataPath
from ndatautils.fileloader import CascadeLoader
from ndatautils.instrumentloader import RESEDALoader
from ndatautils.utils import sine
from ndatautils.miezefitter.reductionjob import ROIReductionJob, ReductionJobResult
from ndatautils.miezefitter.sinefitter import SineFitter, lmfit_backend_fitting
from ndatautils.miezefitter.dreduction import Reduction, ReductionStructure
#------------------------------------------------------------------------------

def test_reductionjob_setup():
    sf = SineFitter(lmfit_backend_fitting)
    assert isinstance(sf, SineFitter)
    rj = ROIReductionJob(sf, job_kwargs={"lrbt" : [20, 25, 54, 75]})
    assert isinstance(rj, ROIReductionJob)

#------------------------------------------------------------------------------

def test_lmfit_SineFitter():
    sf = SineFitter(lmfit_backend_fitting)
    # preparing some sine data
    # some random variation (hardcoded gaussian noise on "y")
    pkeys = ["A", "omega", "phi", "y0"]
    vals = [200, np.pi/8, np.pi/3, 300] # used to produce yrand
    x = np.arange(16)
    yrand = [
        508, 484, 481, 435, 417, 284, 275, 168, 130,  99, 121, 116, 195, 267, 373, 399
    ]
    # assert result
    sfr = sf.fit(x, yrand, np.sqrt(yrand))
    correct_result_flag = np.allclose([sfr.resdict["raw_fit_vals"][k] for k in pkeys], vals, rtol=0.05)
    print(sfr.resdict["raw_fit_vals"])
    print(correct_result_flag)
    assert correct_result_flag

#------------------------------------------------------------------------------

def test_reduction_analysis():
    cdp = CustomDataPath("./testdata/00147720.tof")
    RLoader = RESEDALoader("tof")
    RLoader.set_Loader_settings(foils=[0, 1, 2, 3, 4, 5])
    RCLoader = CascadeLoader(cdp, RLoader)

    sf = SineFitter(lmfit_backend_fitting)
    rj = ROIReductionJob(
        sf,
        job_kwargs={"lrbt" : [20, 25, 54, 75]},
        result_kwargs={
            "key" : "selectiveaverage",
            "foilsidx" : [0,2,3]
        }
    )
    robj = Reduction(RCLoader, rj, False)
    assert isinstance(robj, Reduction)
    assert robj.rawdata.shape == (6,16,128,128)
    assert not robj.rawdata.sum() == 0.0

    assert robj.reductionjobresult == None
    robj.run()
    assert isinstance(robj.reductionjobresult, ReductionJobResult)
    print("\nFinished!\n")

#------------------------------------------------------------------------------

def test_reductionstructure():
    cdp = CustomDataPath("./testdata/00147720.tof")
    RLoader = RESEDALoader("tof")
    RLoader.set_Loader_settings(foils=[0, 1, 2, 3, 4, 5])
    RCLoader = CascadeLoader(cdp, RLoader)

    sf = SineFitter(lmfit_backend_fitting)
    rj = ROIReductionJob(
        sf,
        job_kwargs={"lrbt" : [20, 25, 54, 75]},
        result_kwargs={
            "key" : "selectiveaverage",
            "foilsidx" : [0,2,3]
        }
    )
    robj = Reduction(RCLoader, rj, False)

    rs1 = ReductionStructure(robj)
    assert isinstance(rs1, ReductionStructure)
    # as alternate constructor
    compnents = ((RCLoader, rj, False), (RCLoader, rj, False), (RCLoader, rj, False))
    rs2 = ReductionStructure.from_tuple(*compnents)
    assert len(rs2.red_list) == 3

    rs1.analyze(param_keys={})
    rs2.analyze(param_keys={})