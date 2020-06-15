import pytest
#----------------------------------------------------------
from ndatautils.datapath import CustomDataPath
from ndatautils.fileloader import CascadeLoader
from ndatautils.instrumentloader import RESEDALoader, InstrumentLoader
#----------------------------------------------------------

def test_loading_pad():
    cdp = CustomDataPath("./testdata/00147720.tof")
    RLoader = RESEDALoader('tof')
    assert isinstance(RLoader, InstrumentLoader)
    RCLoader = CascadeLoader(cdp, RLoader)
    RCLoader.read_out_data(False)
    assert RCLoader.datadict["rawdata"].shape == (8, 16, 128, 128)
    assert RCLoader.datadict["rawdata"].sum() == 19271934