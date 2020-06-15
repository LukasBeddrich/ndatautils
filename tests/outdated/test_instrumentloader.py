import numpy as np
#----------------------------------------------------------
from pprint import pprint
from sys import path
#----------------------------------------------------------
from ndatautils.datapath import DataPath
from ndatautils.fileloader import ASCIILoader
from ndatautils.instrumentloader import InstrumentLoader, RESEDALoader
#-----------------------------------------------------------------------------

""" Check the InstrumentLoader class first"""
ILoader = InstrumentLoader()

#-----------------------------------------------------------------------------

""" Print the standard attribute first """
keys = ('metadata', 'rawdata', 'array_format')
for key in keys:
    print("Default setting for ILoader-{} : {}\n".format(key, ILoader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Check if the dtype can be constructed from following first array line"""
first_array_line = np.array(['5.7', '301.661', ';', '5.00', '161027', '20414', '28634', 'cascade/00144328.pad'])#, dtype = "S20")
names = ['etime', 'T', ";", 'timer', 'monitor1', 'psd_channel.roi', 'psd_channel.total', 'file1']

print("Dtype of the data : {}\n".format(ILoader.dtype_from_string_array(first_array_line, names)))
print("Is it saved correctly? -> {}\n".format(ILoader.get_Loader_settings("array_format")))

#-----------------------------------------------------------------------------

""" Check RESEDALoader class next """
RLoader = RESEDALoader('DAT', array_format = ILoader.get_Loader_settings("array_format"))
RLoader.set_Loader_settings(metadata = False)

for key in keys:
    print("Setting for RLoader-{} : {}\n".format(key, RLoader.get_Loader_settings(key)))

#-----------------------------------------------------------------------------

""" Testing the direct call of the Settings via RLoader(*keys) """
print("Setting for RLoader-{} : {}\n".format(keys, RLoader(*keys)))
