from pprint import pprint
from sys import path
#----------------------------------------------------------
path_ndatautils = "/home/lbeddric/Dokumente/devpython/ndatautils"
if path_ndatautils  not in path:
    path.append(path_ndatautils)
#----------------------------------------------------------
from ndatautils.datapath import DataPath
from ndatautils.fileloader import CascadeLoader
#----------------------------------------------------------

instrument = "MIRA"
root = "/home/lbeddric/Dokumente/Data/MIRAdata"
propnum = 13524
ending = ".tof"

#-----------------------------------------------------------------------------

MIRApath = DataPath(instrument, propnum, root, ending)
print(MIRApath(298077), "\n")

#-----------------------------------------------------------------------------

MIRAloader = CascadeLoader(MIRApath)
print("MIRAloader initialized!\nRetrieve data now!")

#-----------------------------------------------------------------------------

MIRAloader.read_out_data(298077)
print("Print some of the metadata now:\n")
pprint(MIRAloader.datadict["metadata"]["Sample and alignment"])

#-----------------------------------------------------------------------------

print("\nShape and total counts of the retrieved rawdata:")
print(MIRAloader.datadict["rawdata"].shape, MIRAloader.datadict["rawdata"].sum())
