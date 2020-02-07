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

import os
import re
import json
import numpy as np
from .datapath import DataPath

class InstrumentLoader:
    """
    Base class for specialized InstrumentLoader classes (MIRALoader, RESEDALoader, ...)
    """

    def __init__(self, metadata = True, rawdata = True, array_format = None, **kwargs):
        """
        Initializes a InstumentLoader instance

        Parameters
        ----------
        metadata : bool, dict, str
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> has to specify which values to select, by specifying the 
            correct main and subkeys of a "loader-object".datadict["metadata"]
            str -> path to a json-formatted metadata_alias file from which the dictionary
            can be recovered
        rawdata : bool
            triggers return of all metadata values (True) or none (False)
        array_format : None, tuple, "Whatever is necessary to define a structured array"
        kwargs : additional settings to specify a loader-objects output

        Returns
        -------

        Notes
        -----
        """

        self.instance_dict = {"metadata" : self.__process_metadata(metadata),
                              "rawdata"  : rawdata,
                              "array_format" : array_format}
        self.set_Loader_settings(**kwargs)

#---------------------------------------------------------------------------------------------------

    def __process_metadata(self, metadata):
        """
        Checks for validity of the passed metadata. Loads dict from json-formatted metadata_alias file.

        Parameters
        ----------
        metadata : bool, dict, str
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> has to specify which values to select, by specifying the 
            correct main and subkeys of a "loader-object".datadict["metadata"]
            str -> path to a json-formatted metadata_alias file from which the dictionary
            can be recovered

        Returns
        -------
        ret : bool, dict
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> specifies which values to select, by specifying the 
            correct main- and subkeys of a "loader-object".datadict["metadata"]
        """

        if isinstance(metadata, bool):
            return metadata
        elif isinstance(metadata, dict): # Possibility to check the dictionary for having a valid structure
            return metadata
        elif isinstance(metadata, str):
            with open(metadata, 'r') as jsonfile:
                meta_aliases = json.load(jsonfile)
            return meta_aliases
        else:
            print("No valid Input was provided as setting for metadata. 'False' was returned!")
            return False

#---------------------------------------------------------------------------------------------------

    def __call__(self, *args):
        """
        Returns the values corresponding to the keys supplied by args

        Parameters
        ----------
        args : str
            keys to querry the instances_dictionary for associated values

        Returns
        -------
        querried : dict
            dictionary of the querried values
        """

        return self.get_Loader_settings(*args)

#---------------------------------------------------------------------------------------------------

    def get_Loader_settings(self, *args):
        """
        Returns the values corresponding to the keys supplied by args

        Parameters
        ----------
        args : str
            keys to querry the instances_dictionary for associated values
            
        Returns
        -------
        querried : dict
            dictionary of the querried values
        """

        querried = []

        for key in args:
            try:
                querried.append((key, self.instance_dict[key]))
            except KeyError:
                print("No value can be found for key: '{}'".format(key))
                querried.append((key, None))

        if len(querried) == 1:
            return querried[0][1] # returnind only the value seems more sensible...
        else:
            return dict(querried)

#---------------------------------------------------------------------------------------------------

    def set_Loader_settings(self, **kwargs):
        """
        Updates the settings (entries) in the self.instance_dict

        Parameters
        ----------
        kwargs : additional settings to specify a loader-objects output
        """

        self.instance_dict.update(dict(kwargs))

#---------------------------------------------------------------------------------------------------

    def dtype_from_string_array(self, first_line, scan_data_names):
        """
        Generates a numpy.dtype object from the first line of the ".dat" file data set.

        Parameters
        ----------
        first_line : numpy.ndarray with dtype = bytes
        scan_data_names : list (with strings)

        Returns
        -------
        dt : numpy.dtype
            specifies the format of the data read by a ASCIILoader

        Notes
        -----
        """

        formats = []
        for val in first_line:
            if re.match("[+-]?\d+$", val) is not None:              # if re.match("[+-]?\d+$", val.decode("utf-8")) is not None:
                formats.append("i8")
            elif re.match("[+-]?\d+[\.e+-]{0,2}\d*", val) is not None:            # elif re.match("[+-]?\d+[\.e+-]{0,2}\d*", val.decode("utf-8")) is not None:
                formats.append('f8')
            else:
                formats.append('S{}'.format(len(val)))
#        print("formats for dtype : {} (type = {})\t\t DEBUGGING".format(formats, type(formats)))
        self.instance_dict['array_format'] = np.dtype({'names' : scan_data_names,
                                                       'formats' : formats})
        return self.instance_dict['array_format']

#---------------------------------------------------------------------------------------------------

####################################################################################################
####################################################################################################
####################################################################################################

class RESEDALoader(InstrumentLoader):
    """
    Subclass of InstrumentLoader dedicated to the RESEDA instrument at FRM II
    """

    def __init__(self, mode, metadata = True, rawdata = True, array_format = None, **kwargs):
        """
        Initializes a RESEDALoader instance

        Parameters
        ----------
        mode : str
            SANS, PAD - mode for '.pad' files
            TOF - mode for '.tof' files
            DAT - mode for '.dat' files
        metadata : bool, dict
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> has to specify which values to select, by specifying the 
            correct main and subkeys of a "loader-object".datadict["metadata"]
        rawdata : bool
            triggers return of all metadata values (True) or none (False)
        kwargs : additional settings to specify a loader-objects output

        Returns
        -------

        Notes
        -----
        """

        if mode.upper() == "TOF":
            super(RESEDALoader, self).__init__(metadata, rawdata, (8, 16, 128, 128), **kwargs)
            self.mode = mode

        elif mode.upper() == "SANS" or mode.upper() == "PAD":
            super(RESEDALoader, self).__init__(metadata, rawdata, (128, 128), **kwargs)
            self.mode = mode

        elif  mode.upper() == "DAT":
            super(RESEDALoader,self).__init__(metadata, rawdata, array_format, **kwargs)
            # HERE I NEED TO FIND A SOLUTION FOR SETTING THE CORRECT 'dtype' OBJECT FOR THE CURRENT DAT-FILE
            self.mode = mode
        else:
            raise ValueError("No proper 'mode' could be set.")

####################################################################################################
####################################################################################################
####################################################################################################

class MIRALoader(InstrumentLoader):
    """
    Subclass of InstrumentLoader dedicated to the RESEDA instrument at FRM II
    """

    def __init__(self, mode, metadata = True, rawdata = True, **kwargs):
        """
        Initializes a MIRALoader instance

        Parameters
        ----------
        mode : str
            SANS, PAD - mode for '.pad' files
            TOF - mode for '.tof' files
            DAT - mode for '.dat' files
        metadata : bool, dict
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> has to specify which values to select, by specifying the 
            correct main and subkeys of a "loader-object".datadict["metadata"]
        rawdata : bool
            triggers return of all metadata values (True) or none (False)
        kwargs : additional settings to specify a loader-objects output

        Returns
        -------

        Notes
        -----
        """

        if mode.upper() == "TOF":
            super(MIRALoader, self).__init__(metadata, rawdata, (8, 16, 128, 128), **kwargs)
            self.mode = mode

        elif mode.upper() == "PAD":
            super(MIRALoader, self).__init__(metadata, rawdata, (128, 128), **kwargs)
            self.mode = mode

        elif  mode.upper() == "DAT":
            super(MIRALoader,self).__init__(metadata, rawdata, None, **kwargs)
            # HERE I NEED TO FIND A SOLUTION FOR SETTING THE CORRECT 'dtype' OBJECT FOR THE CURRENT DAT-FILE
            self.mode = mode

####################################################################################################
####################################################################################################
####################################################################################################

class PANDALoader(InstrumentLoader):
    """
    Subclass of InstrumentLoader dedicated to the RESEDA instrument at FRM II
    """

    def __init__(self, mode, metadata = True, rawdata = True, **kwargs):
        """
        Initializes a MIRALoader instance

        Parameters
        ----------
        mode : str
            DAT - mode for '.dat' files
        metadata : bool, dict
            bool -> values trigger return of all metadata values (True) or none (False)
            dict -> has to specify which values to select, by specifying the 
            correct main and subkeys of a "loader-object".datadict["metadata"]
        rawdata : bool
            triggers return of all metadata values (True) or none (False)
        kwargs : additional settings to specify a loader-objects output

        Returns
        -------

        Notes
        -----
        """

        if mode.upper() == "DAT":
            super(PANDALoader, self).__init__(metadata, rawdata, None, **kwargs)
            self.mode = mode

        else:
            print("No valid mode was chosen!")
            raise ValueError("The {}-mode is not recognized as a valid option.".format(mode))

####################################################################################################
####################################################################################################
####################################################################################################