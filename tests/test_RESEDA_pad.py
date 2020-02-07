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

instrument = "RESEDA"
root = "/home/lbeddric/Dokumente/Data/RESEDAdata"
propnum = 14891
ending = ".pad"
#-----------------------------------------------------------------------------

RESEDApath = DataPath(instrument, propnum, root, ending)
print(RESEDApath(144052), "\n")

#-----------------------------------------------------------------------------

RESEDAloader = CascadeLoader(RESEDApath)
print("RESEDAloader initialized!\nRetrieve data now!")

#-----------------------------------------------------------------------------

RESEDAloader.read_out_data(144052)
print("Print some of the metadata now:\n")
pprint(RESEDAloader.datadict["metadata"]["Sample and alignment"])

#-----------------------------------------------------------------------------

print("\nShape and total counts of the retrieved rawdata:")
print(RESEDAloader.datadict["rawdata"].shape, RESEDAloader.datadict["rawdata"].sum())
