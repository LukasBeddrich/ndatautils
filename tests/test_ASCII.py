import numpy as np
#----------------------------------------------------------
from pprint import pprint
from sys import path
#----------------------------------------------------------
path_ndatautils = "/home/lbeddric/Dokumente/devpython/ndatautils"
if path_ndatautils  not in path:
    path.append(path_ndatautils)
#----------------------------------------------------------
from ndatautils.datapath import DataPath
from ndatautils.fileloader import ASCIILoader
from ndatautils.instrumentloader import InstrumentLoader, RESEDALoader
#----------------------------------------------------------

instrument = "RESEDA"
root = "/home/lbeddric/Dokumente/Data/RESEDAdata"
propnum = 14891
ending = ".dat"

#-----------------------------------------------------------------------------

RESEDApath = DataPath(instrument, propnum, root, ending)
print(RESEDApath(4408), "\n")

#-----------------------------------------------------------------------------

""" Check the initialization of a ASCIILoader object """
R1_ASCIILoader = ASCIILoader(RESEDApath)
print("R1_ASCIILoader initialized!\nRetrieve data now!")

#-----------------------------------------------------------------------------

""" Setting 'rawdata' to False so ne issues occure during read_out_data """
R1_ASCIILoader.rawdata = False
print("'rawdata' setting : {}".format(R1_ASCIILoader.rawdata))

#-----------------------------------------------------------------------------

""" Printing some of the 'metadata' """
R1_ASCIILoader.read_out_data(4408)
print("Print some of the metadata now:\n")
pprint(R1_ASCIILoader.datadict["metadata"]["Scan data"])
print("As expected the 'rawdata' output = {}".format(R1_ASCIILoader.datadict['rawdata']))

#-----------------------------------------------------------------------------

""" Try to get proper data from ASCII-file -> create propper RESEDALoader instance """
print("Try to get proper data from ASCII-file -> create propper with a RESEDALoader instance")
RLoader = RESEDALoader("DAT")
keys = ('metadata', 'rawdata', 'array_format')
for key in keys:
    print("Default setting for RLoader-{} : {}\n".format(key, RLoader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Pass the RLoader to a new ASCIILoader and access the RLoaders properties within R2_ASCIILoader """
R2_ASCIILoader = ASCIILoader(RESEDApath, RLoader)
#R2_ASCIILoader.instrumentloader.set_Loader_settings(rawdata = False)
for key in keys:
    print("Default setting for RLoader-{} : {}\n".format(key, R2_ASCIILoader.instrumentloader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Load the data of a ".dat" file """
R2_ASCIILoader.read_out_data(4408)
print("Data successfully loaded?")
print(R2_ASCIILoader.datadict['metadata']['Scan data'])
print(R2_ASCIILoader.datadict['rawdata']['file1'][:5])
print(R2_ASCIILoader.instrumentloader.get_Loader_settings("array_format"))

#-----------------------------------------------------------------------------

