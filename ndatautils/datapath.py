# -*- coding: utf-8 -*-

from os import path

class DataPath:
    """
    Class to generate the appropriate path to a data file condidering instrument, proposal and file type
    as used by NICOS instrument control software
    """
    
    def __init__(self, instrument, proposalnum, root, ending = ".dat"):
        """
        Initializes a DataPath instance.
        """

        if instrument.upper() == "MIRA":
            self.instrument = "MIRA"
        elif instrument.upper() == "RESEDA":
            self.instrument = "RESEDA"
        elif instrument.upper() == "KOMPASS":
            self.instrument = "KOMPASS"
        elif instrument.upper() == "PANDA":
            self.instrument = "PANDA"
        elif instrument.upper() == "NLAUE":
            self.instrument = "NLAUE"
        else:
            print("The specified instrument is not recognized. Expected inputs are:\n\t'MIRA' \n\t'RESEDA' \n\t'KOMPASS' \ņ\t'NLAUE'")
        
        self.root = root
        self.proposalnum = proposalnum
        self.ending = ending

#---------------------------------------------------------------------------------------------------

    def __call__(self, fnum):
        """
        Calls the 'gen_path' method.
        """

        return self.gen_path(fnum)

#---------------------------------------------------------------------------------------------------

    def gen_path(self, fnum):
        """
        Returns the path of a specified datafile by its filenumber. Hands task to correct path generator
        """

        if self.instrument == "MIRA":
            return self.__gen_path_MIRA(fnum)

        elif self.instrument == "RESEDA":
            return self.__gen_path_RESEDA(fnum)

        elif self.instrument == "KOMPASS":
            return self.__gen_path_KOMPASS(fnum)

        elif self.instrument == "PANDA":
            return self.__gen_path_PANDA(fnum)

        elif self.instrument == "NLAUE":
            return self.__gen_path_NLAUE(fnum)

#---------------------------------------------------------------------------------------------------

    def __gen_path_MIRA(self, fnum):
        """
        Generates the path for a MIRA-type ASCII data file or MIEZE-TOF file.
        """

        if self.ending == ".dat":
            return path.join(self.root, str(self.proposalnum), "data", str(self.proposalnum) + "_%08d" %(fnum) + ".dat")
        
        elif self.ending == ".tof":
            return path.join(self.root, str(self.proposalnum), "data", "cascade", "%08d"%(fnum) + ".tof")
        
        elif self.ending == ".pad":
            return path.join(self.root, str(self.proposalnum), "data", "cascade", "%08d"%(fnum) + ".pad")

        else:
            print("No valid file ending!")
            return None

#---------------------------------------------------------------------------------------------------
        
    def __gen_path_RESEDA(self, fnum):
        """
        Generates the path for a RESEDA-type ASCII data file, MIEZE-TOF file, CASCADE-PAD file.
        """

        if self.ending == ".dat":
            return path.join(self.root, "p{}".format(self.proposalnum), "data","p{}".format(self.proposalnum) + "_%08d" %(fnum) + ".dat")

        elif self.ending == ".tof":
            return path.join(self.root, "p{}".format(self.proposalnum), "data" , "cascade", "%08d" %(fnum) + ".tof")

        elif self.ending == ".pad":
            return path.join(self.root, "p{}".format(self.proposalnum), "data" , "cascade", "%08d" %(fnum) + ".pad")

        else:
            print("No valid file ending!")
            return None

#---------------------------------------------------------------------------------------------------

    def __gen_path_KOMPASS(self, fnum):
        """
        Not yet implemented
        Generates the path for a KOMPASS-type ASCII data file
        """

        print("Path generation for KOMPASS data is not yet implemented.")
        return None

#---------------------------------------------------------------------------------------------------
        
    def __gen_path_PANDA(self, fnum):
        """
        Generates the path for a RESEDA-type ASCII data file, MIEZE-TOF file, CASCADE-PAD file.
        """

        if self.ending == ".dat":
            return path.join(self.root, "p{}".format(self.proposalnum), "data","p{}".format(self.proposalnum) + "_%08d" %(fnum) + ".dat")

        else:
            print("No valid file ending!")
            return None

#---------------------------------------------------------------------------------------------------

    def __gen_path_NLAUE(self, fnum):
        """
        Not yet implemented
        Generates the path for a NLAUE-type
        """

        print("Path generation for NLAUE data is not yet implemented.")
        return None
        
#---------------------------------------------------------------------------------------------------

####################################################################################################
####################################################################################################
####################################################################################################

class CustomDataPath(DataPath):
    """
    DataPath subclass that allows to give path to a data file which does not obey
    the standard directory structure defined in ndatautils.datapath.DataPath
    """
    def __init__(self, custompath):
        """
        Parameters
        ---------
        custompath : str
            path of a custom specified data file
        """
        self.custompath = custompath

#---------------------------------------------------------------------------------------------------
    def gen_path(self, other_path=False):
        """
        Allows 

        Parameters
        ---------
        other_path : str
            path of another custom specified data file
        """
        if other_path:
            return other_path
        else:
            return self.custompath