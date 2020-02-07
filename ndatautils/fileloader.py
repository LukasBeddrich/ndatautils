# -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the ndatautils contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Lukas Beddrich <lukas.beddrich@frm2.tum.de>
#
# *****************************************************************************

import re
import numpy as np
from .datapath import DataPath

####################################################################################################
####################################################################################################
####################################################################################################

class FileLoaderBase:
    """
    Base class for loading the data from specified file
    """

    def __init__(self, datapath, instrumentloader = None):
        """
        Initializes a FileLoaderBase instance

        Parameters
        ----------
        datapath : DataPath
            DataPath object to retrieve the required file name via datapath(fnum)
            The file needs to be a '.tof' or '.pad' file as created by NICOS from
            a CASCADE detector's output.
        instrumentloader: InstrumentLoader, a subclass
            Not yet implemented

        Returns
        -------

        Notes
        -----
        """

        self.datadict = {}
        self.datapath = datapath
        if instrumentloader == None:
            self.metadata = True                    # Workaround until InstrumentLoader(s) are implemented
            self.rawdata = True                     # Workaround until InstrumentLoader(s) are implemented
            self.instrumentloader = None
        else:
            self.instrumentloader = instrumentloader

#---------------------------------------------------------------------------------------------------

    def __call__(self, fnum, metadata = True, rawdata = True):
        """
        Instance calls the read_out_data method
        """

        return self.read_out_data(fnum)

#---------------------------------------------------------------------------------------------------

    def _meta_data(self, fnum):
        """
        Extracts metadata from a file. If some quantities are specified in a
        self.metadata dictionary, only their values are retrieved
        Dictionary key formating is possible if necesary information is provided
        
        Parameters
        ----------
        fnum : int (, str)
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> Specification of retrieved metadata
        --> providing aliases for formating klunky key-strings in metadict
        """

        print("This is the FileLoaderBase._meta_data function, which does not provide functionality.\
              The function needs to be overloaded by a subclass")
        return {'requested data' : 'None'}

#---------------------------------------------------------------------------------------------------

    def _raw_data(self, fnum):
        """
        Extracts rawdata from a file. If a array shape is specified in a
        self.rawdata tuple, and the returned array is shaped accordingly
        MAYBE a fucntionality for summation over some axis will be added here as well

        Parameters
        ----------
        fnum : int (, str)
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> summation or mean calculation on the raw data
        """

        print("This is the FileLoaderBase._raw_data function, which does not provide functionality.\
              The function needs to be overloaded by a subclass")
        return {'requested data' : 'None'}

#---------------------------------------------------------------------------------------------------

    def format_metadata(self):
        """
        Restructures self.datadict["metadata"]. Selects and possibly renames the metadata keys
        according to specifications in self.instrumentloader.instance_dict['metadata'].
        
        Notes
        -----
        self.instrumentloader.get_Loader_settings('metadata') --> {'mainkey1' : [[subkey1, None], [subkey2, alias2],
                                                                                 [subkey3, alias3], ...],
                                                                   'mainkey2' : [[subkey1, alias1], [subkey2, None],
                                                                                 [subkey3, alias3], ...], ...}
        """

        tempdict = {}
        for mainkey in self.instrumentloader.get_Loader_settings('metadata'):
            tempdict[mainkey] = {}
            for subkey, alias in self.instrumentloader.get_Loader_settings('metadata')[mainkey]:
                if alias != None:
                    tempdict[mainkey][alias] = self.datadict[mainkey][subkey]
                else:
                    tempdict[mainkey][subkey] = self.datadict[mainkey][subkey]

        self.datadict['metadict'] = tempdict

#---------------------------------------------------------------------------------------------------

    def read_out_data(self, fnum):
        """
        Updates the datadict with the metadata and rawdata (as specified via instrumentloader) for a
        file with number fnum.
        For specifics refer to subclass._meta_data and subclass._raw_data
        """

        if self.instrumentloader is not None:
            if isinstance(self.instrumentloader.get_Loader_settings('metadata'), dict):
                self.datadict.update({'metadata' : self._meta_data(fnum)})
                self.format_metadata()
            elif self.instrumentloader.get_Loader_settings('metadata'):
                self.datadict.update({'metadata' : self._meta_data(fnum)})
            else:
                self.datadict.update({'metadata' : {'requested data' : 'None'}})

            if isinstance(self.instrumentloader.get_Loader_settings('rawdata'), tuple):
                self.datadict.update({'rawdata'  : self._raw_data(fnum)})
            elif self.instrumentloader.get_Loader_settings('rawdata'):
                self.datadict.update({'rawdata'  : self._raw_data(fnum)})
            else:
                self.datadict.update({'rawdata' : {'requested data' : 'None'}})


        else:
            if self.metadata:
                self.datadict.update({'metadata' : self._meta_data(fnum)})
            else:
                self.datadict.update({'metadata' : {'requested data' : 'None'}})

        # THIS PART NEEDS MAJOR REWORKS DUE TO USAGE OF STRUCTURED ARRAYS
            if self.rawdata:
                self.datadict.update({'rawdata'  : self._raw_data(fnum)})
            else:
                self.datadict.update({'rawdata' : {'requested data' : 'None'}})

#---------------------------------------------------------------------------------------------------

####################################################################################################
####################################################################################################
####################################################################################################

class CascadeLoader(FileLoaderBase):
    """
    Loads data from '.tof' and '.pad' files from the CASCADE detector used at MIRA and RESEDA.
    """

#---------------------------------------------------------------------------------------------------

    def _meta_data(self, fnum):
        """
        Extracts metadata from a ".pad" or ".tof" file. If some quantities are specified in a
        self.metadata dictionary, only their values are retrieved
        Dictionary key formating is possible if necesary information is provided
        
        Parameters
        ----------
        fnum : int
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> Specification of retrieved metadata
        --> providing aliases for formating klunky key-strings in metadict
        """

        valuereo = re.compile("[+-]?\d+[\.e+-]{0,2}\d*")
        unitreo = re.compile("\s[A-Za-z]{1,4}[\-\d]{0,2}$") # strip " "

        currentkey = "binarydump"
        metadict = {currentkey : {}}
        with open(self.datapath(fnum), "rb") as f:

            for line in f.readlines():
                try:
                    temp = line.decode("utf-8").strip().split(':')
                except:
                    pass

                if len(temp) == 1 and temp[0][:3] == "###":
                    currentkey = temp[0][3:].strip()
                    metadict[currentkey] = {}

                elif len(temp) == 2:
                    val_result = valuereo.findall(temp[1])
                    unit_result = unitreo.findall(temp[1])

                    if len(val_result) == 1 and len(unit_result) != 0:
                        metadict[currentkey][temp[0].strip()] = (float(val_result[0]), unit_result[0].strip())

                    elif len(val_result) > 1 and len(unit_result) != 0:
                        metadict[currentkey][temp[0].strip()] = (tuple((float(val) for val in val_result)), unit_result[0].strip())

                    elif len(val_result) > 1 and len(unit_result) == 0:
                        try:
                            metadict[currentkey][temp[0].strip()] = tuple((float(val) for val in val_result))
                        except ValueError:
                            metadict[currentkey][temp[0].strip()] = tuple((val for val in val_result))                            

                    elif len(val_result) == 1 and len(unit_result) == 0:
                        try:
                            metadict[currentkey][temp[0].strip()] = int(val_result[0])
                        except ValueError:
                            try:
                                metadict[currentkey][temp[0].strip()] = float(val_result[0])
                            except:
                                print("The encountered 'val_result' was neither a integer as string, nor a flaotable string")
                                raise

                    else:
                        metadict[currentkey][temp[0].strip()] = temp[1].strip()

                elif len(temp) == 3:
                    if temp[1].strip() == "http" or temp[1].strip() == "https":
                        metadict[currentkey][temp[0].strip()] = ":".join((temp[1], temp[2]))
                    else:
                        metadict[currentkey][temp[0].strip()] = (temp[1].strip(), temp[2].strip())

                elif len(temp) == 4:
                    metadict[currentkey][temp[0].strip()] = (temp[1].strip(), " : ".join((temp[2].strip(), temp[3].strip())))

        del metadict["binarydump"]            
        return metadict

#---------------------------------------------------------------------------------------------------

    def _raw_data(self, fnum):
        """
        Extracts rawdata from a ".pad" or ".tof" file. If a array shape is specified in a
        self.rawdata tuple, and the returned array is shaped accordingly
        MAYBE a fucntionality for summation over some axis will be added here as well

        Parameters
        ----------
        fnum : int
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> shaping of the data array
        --> summation or mean calculation on the raw data
        """

        try:
            temparr = np.fromfile(self.datapath(fnum), dtype = np.int32)[:128*128*16*8].reshape(8, 16, 128, 128)
        except TypeError:
            temparr = np.fromfile(self.datapath(fnum), dtype = np.int32)[:128*128].reshape(128, 128)
        except ValueError:
            temparr = np.fromfile(self.datapath(fnum), dtype = np.int32)[:128*128].reshape(128, 128)

        return temparr

#---------------------------------------------------------------------------------------------------

    def not_yet_implemented(self):
        """
        
        """
        print("Not yet Implemnted!")

#---------------------------------------------------------------------------------------------------

####################################################################################################
####################################################################################################
####################################################################################################

class ASCIILoader(FileLoaderBase):
    """
    Loads data from '.tof' and '.pad' files from the CASCADE detector used at MIRA and RESEDA.
    """

#---------------------------------------------------------------------------------------------------

    def _meta_data(self, fnum):
        """
        Extracts metadata from a ".pad" or ".tof" file. If some quantities are specified in a
        self.metadata dictionary, only their values are retrieved
        Dictionary key formating is possible if necesary information is provided

        Parameters
        ----------
        fnum : int
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> Specification of retrieved metadata
        --> providing aliases for formating klunky key-strings in metadict
        """

        valuereo = re.compile("[+-]?\d+[\.e+-]{0,2}\d*")
        unitreo = re.compile("\s[A-Za-z]{1,4}[\-\d]{0,2}$") # strip " "

        currentkey = "binarydump"
        metadict = {currentkey : {}}
        with open(self.datapath(fnum), "rb") as f:

            for line in f.readlines():
                try:
                    temp = line.decode("utf-8")[1:].strip().split(':') # [1:] omits the first '#'
                except:
                    pass

                if len(temp) == 1 and temp[0][:2] == "##": # find only '##' because the first one was omitted earlier
                    currentkey = temp[0][2:].strip()
                    metadict[currentkey] = {}

                elif len(temp) == 1 and currentkey == "Scan data":
                    data_aquisition_setting = tuple(re.findall('[A-Za-z0-9\._\-;]+', temp[0]))
                    if len(metadict[currentkey]) == 0:
                        metadict[currentkey]['names'] = data_aquisition_setting
                    elif len(metadict[currentkey]) == 1:
                        metadict[currentkey]['units'] = data_aquisition_setting

                elif len(temp) == 2:
                    val_result = valuereo.findall(temp[1])
                    unit_result = unitreo.findall(temp[1])

                    if len(val_result) == 1 and len(unit_result) != 0:
                        metadict[currentkey][temp[0].strip()] = (float(val_result[0]), unit_result[0].strip())

                    elif len(val_result) > 1 and len(unit_result) != 0:
                        metadict[currentkey][temp[0].strip()] = (tuple((float(val) for val in val_result)), unit_result[0].strip())

                    elif len(val_result) > 1 and len(unit_result) == 0:
                        metadict[currentkey][temp[0].strip()] = tuple((float(val) for val in val_result))

                    elif len(val_result) == 1 and len(unit_result) == 0:
                        try:
                            metadict[currentkey][temp[0].strip()] = int(val_result[0])
                        except ValueError:
                            try:
                                metadict[currentkey][temp[0].strip()] = float(val_result[0])
                            except:
                                print("The encountered 'val_result' was neither a integer as string, nor a flaotable string")
                                raise

                    else:
                        metadict[currentkey][temp[0].strip()] = temp[1].strip()

                elif len(temp) == 3:
                    if temp[1].strip() == "http" or temp[1].strip() == "https":
                        metadict[currentkey][temp[0].strip()] = ":".join((temp[1], temp[2]))
                    else:
                        metadict[currentkey][temp[0].strip()] = (temp[1].strip(), temp[2].strip())

                elif len(temp) == 4:
                    metadict[currentkey][temp[0].strip()] = (temp[1].strip(), " : ".join((temp[2].strip(), temp[3].strip())))

        del metadict["binarydump"]            
        return metadict

#---------------------------------------------------------------------------------------------------

    def _raw_data(self, fnum):
        """
        Extracts array data from '.dat' file

        Parameters
        ----------
        fnum : int
            passed to the self.datapath instance to get path of the data file

        NOT (YET) IMPLEMENTED
        ---------------------
        --> shaping of the data array
        --> summation or mean calculation on the raw data
        """

        data_as_string = np.genfromtxt(self.datapath(fnum), dtype = str)

        if self.instrumentloader != None and self.instrumentloader.get_Loader_settings('array_format') != None:
#            print("For debugging purposes: ",data_as_string[:3]) #DEBUGGING
            return np.array(list(zip(*data_as_string.T)), dtype = self.instrumentloader.get_Loader_settings('array_format'))
        elif self.instrumentloader:
            try:
                names = self.datadict['metadata']['Scan data']['names']
            except KeyError:
                self.datadict.update({'metadata' : self._meta_data(fnum)})
                names = self.datadict['metadata']['Scan data']['names']

            dtype = self.instrumentloader.dtype_from_string_array(data_as_string[0], names)

            return np.array(list(zip(*data_as_string.T)), dtype = dtype)
        else:
            raise IOError("The data format is not correctly specified!")

#---------------------------------------------------------------------------------------------------

    def fnums_from_structured_array(self):
        """
        Returns the file numbers 'fnum' gathered in a ASCII file's strucutred array
        """

        if self.datadict:
            try:
                return [int(re.findall('\d+', struct_line[-1].decode("utf-8"))[0]) for struct_line in self.datadict['rawdata']]
            except KeyError:
                print("Probaly self.datadict['rawdata'] is non-exsistant!")
            except AttributeError:
                print("Probaly no proper entries in self.datadict['rawdata'] for decoding or conversion to integer!")

        else:
            print("So far no data was loaded in the self.datadict variable.")

#---------------------------------------------------------------------------------------------------

####################################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


def _all_metadata(path, num):
    """
    processes metadata from a (RESEDA) PAD or TOF file
    """
    
    valuereo = re.compile("[+-]?\d+[\.e+-]{0,2}\d*")
    unitreo = re.compile("\s[A-Za-z]{1,4}$") # strip " "
    
    currentkey = "binarydump"
    metadict = {currentkey : {}}
    with open(path(num)) as f:
        
        for line in f.readlines():
            temp = line.strip().split(':')
            
            if len(temp) == 1 and temp[0][:3] == "###":
                currentkey = temp[0][3:].strip()
                metadict[currentkey] = {}
                
            elif len(temp) == 2:
                val_result = valuereo.findall(temp[1])
                unit_result = unitreo.findall(temp[1])
                
                if len(val_result) == 1 and len(unit_result) != 0:
                    metadict[currentkey][temp[0].strip()] = (float(val_result[0]), unit_result[0])
                    
                elif len(val_result) > 1 and len(unit_result) != 0:
                    metadict[currentkey][temp[0].strip()] = (tuple((float(val) for val in val_result)), unit_result[0])
                    
                elif len(val_result) > 1 and len(unit_result) == 0:
                    metadict[currentkey][temp[0].strip()] = tuple((float(val) for val in val_result))
                    
                elif len(val_result) == 1 and len(unit_result) == 0:
                    try:
                        metadict[currentkey][temp[0].strip()] = int(val_result[0])
                    except ValueError:
                        try:
                            metadict[currentkey][temp[0].strip()] = float(val_result[0])
                        except:
                            print("The encountered 'val_result' was neither a integer as string, nor a flaotable string")
                            raise
                            
                else:
                    metadict[currentkey][temp[0].strip()] = temp[1].strip()
            
            elif len(temp) == 3:
                if temp[1].strip() == "http" or temp[1].strip() == "https":
                    metadict[currentkey][temp[0].strip()] = ":".join((temp[1], temp[2]))
                else:
                    metadict[currentkey][temp[0].strip()] = (temp[1].strip(), temp[2].strip())
                
            elif len(temp) == 4:
                metadict[currentkey][temp[0].strip()] = (temp[1].strip(), " : ".join((temp[2].strip(), temp[3].strip())))
                
    del metadict["binarydump"]            
    return metadict