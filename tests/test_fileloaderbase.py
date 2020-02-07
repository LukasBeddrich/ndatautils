import numpy as np
#----------------------------------------------------------
from pprint import pprint
from sys import path
#----------------------------------------------------------
path_ndatautils = "/home/lbeddric/Dokumente/devpython/ndatautils"
if path_ndatautils  not in path:
    path.append(path_ndatautils)
#---------------------------------------------------------
from ndatautils.datapath import DataPath
from ndatautils.fileloader import *
from ndatautils.instrumentloader import InstrumentLoader, RESEDALoader
#-----------------------------------------------------------------------------

instrument = "RESEDA"
root = "/home/lbeddric/Dokumente/Data/RESEDAdata"
propnum = 14891
ending = ".dat"

#-----------------------------------------------------------------------------

RESEDApath = DataPath(instrument, propnum, root, ending)
print(RESEDApath(4408), "\n")

#-----------------------------------------------------------------------------

""" Check if ASCIILoader is instantiated correctly if subclass of FileLoaderBase (No InstrumentLoader)"""
Ascii1 = ASCIILoader(RESEDApath)
print("Status without instrument loader:\nmetadata setting: {}, rawdata: {}, instrumentloader: {}\n".format(Ascii1.metadata, Ascii1.rawdata, Ascii1.instrumentloader))

#-----------------------------------------------------------------------------

""" Try to get proper data from ASCII-file -> create propper RESEDALoader instance """
RLoader = RESEDALoader("DAT", rawdata = False)

#-----------------------------------------------------------------------------

""" Check if ASCIILoader is instantiated correctly if subclass of FileLoaderBase (With InstrumentLoader)"""
print("Try to get proper data from ASCII-file -> create propper with a RESEDALoader instance")
keys = ('metadata', 'rawdata', 'array_format')
Ascii2 = ASCIILoader(RESEDApath, RLoader)
for key in keys:
    print("Default setting for RLoader-{} : {}\n".format(key, Ascii2.instrumentloader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Check if CascadeLoader is instantiated correctly if subclass of FileLoaderBase (With InstrumentLoader)"""
print("Initialize a CascadeLoader")
Cascade = CascadeLoader(RESEDApath, RLoader)
for key in keys:
    print("Default setting for RLoader-{} : {}\n".format(key, Cascade.instrumentloader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Load the data of a ".dat" file """
Ascii2.read_out_data(4408)
print("Data successfully loaded?")
print(Ascii2.datadict['metadata']['Scan data'])