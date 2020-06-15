import pytest
from ndatautils.datapath import DataPath, CustomDataPath
#------------------------------------------------------------------------------
instrument = "MIRA"
propnum = 14891
root = "/home/lbeddric/Documents/Data/MIRAdata"
ending = ".pad"
#------------------------------------------------------------------------------

def test_MIRA_datapath():
    dp = DataPath(instrument, propnum, root, ending)
    assert isinstance(dp, DataPath)
    assert dp(1234321)  == '/home/lbeddric/Documents/Data/MIRAdata/14891/data/cascade/01234321.pad'

def test_RESEDA_datapath():
    Rdp = DataPath("RESEDA", 14891, "/home/lbeddric/Documents/Data/RESEDAdata", ".tof")
    assert isinstance(Rdp, DataPath)
    assert Rdp.gen_path(432234) == '/home/lbeddric/Documents/Data/RESEDAdata/p14891/data/cascade/00432234.tof'

def test_custompath():
    cdp1 = CustomDataPath("/home/lbeddric/Documents/somedata/datafile1.dat")
    assert isinstance(cdp1, DataPath)
    assert isinstance(cdp1, CustomDataPath)
    assert cdp1.gen_path() == "/home/lbeddric/Documents/somedata/datafile1.dat"
    assert cdp1("/home/lbeddric/Documents/somedata/someotherdatafile1.dat") == "/home/lbeddric/Documents/somedata/someotherdatafile1.dat"
