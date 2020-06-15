import pytest
#----------------------------------------------------------
from ndatautils.datapath import CustomDataPath
from ndatautils.fileloader import CascadeLoader
#----------------------------------------------------------

def test_loading_pad():
    cdp = CustomDataPath("./testdata/00144330.pad")
    RCLoader = CascadeLoader(cdp)
    RCLoader.read_out_data(False)
    assert RCLoader.datadict["rawdata"].shape == (128, 128)
    assert RCLoader.datadict["rawdata"].sum() == 28696