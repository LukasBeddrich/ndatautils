import numpy as np
import pytest
#----------------------------------------------------------
from ndatautils.datapath import CustomDataPath
from ndatautils.fileloader import ASCIILoader
from ndatautils.instrumentloader import RESEDALoader
#----------------------------------------------------------

RESEDAPath = CustomDataPath("./testdata/p14891_00004408.dat")

def test_ASCIILoader_metadata_extraction():
    R1_ASCIILoader = ASCIILoader(RESEDAPath)
    assert R1_ASCIILoader.datadict == {}

    R1_ASCIILoader.rawdata = False
    R1_ASCIILoader.read_out_data(fnum=False) # False, otherwise wrong path to file is returned
    correct_metadata_flag = all([R1_ASCIILoader.datadict["metadata"]["Scan data"]["units"][idx] == x for idx, x in enumerate(('s', 'C', ';', 's', 'cts', 'cts', 'cts', '-'))])
    assert correct_metadata_flag

#-----------------------------------------------------------------------------

def test_ASCII_all_data_extraction():
    RLoader = RESEDALoader("DAT")
    R2_ASCIILoader = ASCIILoader(RESEDAPath, RLoader)
    assert id(R2_ASCIILoader.instrumentloader) == id(RLoader)

    R2_ASCIILoader.read_out_data(fnum=False)
    assert isinstance(R2_ASCIILoader.instrumentloader.get_Loader_settings("array_format"), np.dtype)