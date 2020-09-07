"""

"""
###############################################################################
### IMPORTS
from ast import literal_eval
from numpy import genfromtxt

###############################################################################
### FUNCTIONALITY
def val_to_float(var_val_tuple):
    """
    Used for converison of ("parameter_key", "parameter_value") tuples
    into ("parameter_key", float("parameter_value")).
    """
    try:
        val = float(var_val_tuple[1])
    except:
        val = var_val_tuple[1].strip()
    return var_val_tuple[0].strip(), val

#------------------------------------------------------------------------------

def convertString(s):
    '''
    This function will try to convert a string literal to a number or a bool
    such that '1.0' and '1' will both return 1.

    The point of this is to ensure that '1.0' and '1' return as int(1) and that
    'False' and 'True' are returned as bools not numbers.

    This is useful for generating text that may contain numbers for diff
    purposes.  For example you may want to dump two XML documents to text files
    then do a diff.  In this case you would want <blah value='1.0'/> to match
    <blah value='1'/>.

    The solution for me is to convert the 1.0 to 1 so that diff doesn't see a
    difference.

    If s doesn't evaluate to a literal then s will simply be returned UNLESS the
    literal is a float with no fractional part.  (i.e. 1.0 will become 1)

    If s evaluates to float or a float literal (i.e. '1.1') then a float will be
    returned if and only if the float has no fractional part.

    if s evaluates as a valid literal then the literal will be returned. (e.g.
    '1' will become 1 and 'False' will become False)
    '''


    if isinstance(s, str):
        # It's a string.  Does it represnt a literal?
        #
        try:
            val = literal_eval(s)
        except:
            # s doesn't represnt any sort of literal so no conversion will be
            # done.
            #
            val = s
    else:
        # It's already something other than a string
        #
        val = s

    ##
    # Is the float actually an int? (i.e. is the float 1.0 ?)
    #
    if isinstance(val, float):
        if val.is_integer(): 
            return int(val)

        # It really is a float
        return val

    return val

#------------------------------------------------------------------------------

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

###############################################################################
### LineParser
class PassParser:
    """
    
    """
    def parse(self, key, *parse_string):
        """
        
        """
        return (key.strip().upper(), " ".join([s.strip() for s in parse_string]))

#------------------------------------------------------------------------------

class InstrParser:
    """
    
    """
    def parse(self, key, *parse_strings):
        """
        
        """
        return ("INSTRUMENT", " ".join([to_strip.strip() for to_strip in parse_strings]))

#------------------------------------------------------------------------------

class FileNrParser:
    """
    
    """
    def parse(self, key, parse_string):
        """
        
        """
        try:
            return ("FILENUMBER", int(parse_string))
        except:
            return ("FILENUMBER", parse_string.strip())

#------------------------------------------------------------------------------

class DateParser:
    """
    
    """
    _months = {"JAN" : "01",
               "FEB" : "02",
               "MAR" : "03",
               "APR" : "04",
               "MAY" : "05",
               "JUN" : "06",
               "JUL" : "07",
               "AUG" : "08",
               "SEP" : "09",
               "OCT" : "10",
               "NOV" : "11",
               "DEC" : "12"
              }

    def parse(self, key, *parse_strings):
        """
        
        """
        datehr, minutes, seconds = [s.strip() for s in parse_strings]
        date, hours = datehr.strip().split(" ")
        y, m, d = date.split("-")[::-1]
        m = self._months[m.upper()]
#        retdict = {"DATE" : "/".join([y, m, d]),
#                   "TIME" : ":".join([hours, minutes, seconds])
#                  }
        retdict = ("DATE-TIME", " ".join(("/".join([y, m, d]), ":".join([hours, minutes, seconds]))))
        return retdict

#------------------------------------------------------------------------------

class PosQEParser:
    """
    
    """
    def parse(self, key, parse_string):
        """
        
        """
        qpos = ("QH", "QK", "QL", "EN", "UN")
        vals = [s.split("=")[1].strip() for s in parse_string.strip().split(", ")]
        return ("POSQE", dict(zip(qpos, vals)))

#------------------------------------------------------------------------------

class ParamParser:
    """
    
    """
    def parse(self, key, parse_strings):
        """
        
        """
        varvals = [vv.strip() for vv in parse_strings.split(",")]
        return (key.strip().upper(), dict([val_to_float(vv.split("=")) for vv in varvals]))

#------------------------------------------------------------------------------

class CommandParser:
    """
    
    """
    _idx_allocator = {
        0 : "device_state",
        1 : "step_indicator",
        2 : "step",
        3 : "numpoints_indicator",
        4 : "numpoints",
        5 : "counter_device",
        6 : "counter_threshold"
    }

    def parse(self, key, parse_string):
        """
        
        """
        bits = parse_string.strip().split(" ")
        
        retdict = {
            "command" : bits[0],
            "device" : bits[1],
            "device_state" : [],
            "step_indicator" : None,
            "step" : [],
            "numpoints_indicator" : None,
            "numpoints" : 0,
            "counter_device" : None,
            "counter_threshold" : 0
        }

        a = 0
        for idx, element in enumerate(bits[2:]):
            temp = convertString(element)
            if isinstance(temp, str):
                a += 1
                retdict[self._idx_allocator[a]] = temp
                a += 1
            elif isinstance(temp, int) or isinstance(temp, float):
                if isinstance(retdict[self._idx_allocator[a]], int):
                    retdict[self._idx_allocator[a]] = temp
                elif isinstance(retdict[self._idx_allocator[a]], list):
                    retdict[self._idx_allocator[a]].append(temp)
        return ("COMMAND", retdict)

#------------------------------------------------------------------------------

class DataDescrParser:
    
    def parse(self, data_descr_line):
        return [dev for dev in data_descr_line.split(" ") if (dev != "" and dev != "\n")]

###############################################################################
### IN12Parser

class IN12Parser:
    """
    
    """
    _parsers = {
        "INSTR" : InstrParser(),
        "EXPNO" : PassParser(),
        "USER_" : PassParser(),
        "LOCAL" : PassParser(),
        "FILE_" : FileNrParser(),
        "DATE_" : DateParser(),
        "TITLE" : PassParser(),
        "TYPE_" : PassParser(),
        "COMND" : CommandParser(),
#        "POSQE" : PosQEParser(),
        "POSQE" : ParamParser(),
        "CURVE" : PassParser(),
        "STEPS" : ParamParser(),
        "PARAM" : ParamParser(),
        "VARIA" : ParamParser(),
        "ZEROS" : ParamParser(),
        "ELSE_" : PassParser(),
        "DATAD" : DataDescrParser()
    }
    
    def _get_neutron_data(self, filepath, headerlength=0):
        return genfromtxt(filepath, skip_header=headerlength)

    def parse(self, filepath):
        """
        
        """
        meta_dict = {}
        at_data = False
        linecounter = 0     

        with open(filepath, "r") as f:
            # read lines as lon as "DATA_" specifier in file is not reached
            while not at_data:
                linecounter += 1
                line = f.readline()
                splitted = line.split(":")
                key = splitted[0]
                # skip as long as line does not start with 5 char keyword
                if len(key) != 5:
                    continue
                # if line starts with known keyword -> parse accordingly
                elif key in self._parsers.keys():
                    retkey, retdict = self._parsers[key].parse(*splitted)
                    if retkey in meta_dict.keys():
                        meta_dict[key].update(retdict)
                    else:
                        meta_dict[key] = retdict
                elif key == "DATA_":
                    data_descr_line = f.readline()
                    device_names = DataDescrParser().parse(data_descr_line)
                    at_data = True
        _data = self._get_neutron_data(filepath, linecounter + 1)
        return MetaDataContainer(meta_dict), NeutronDataContainer(_data, colnames=device_names, units=[""] * len(device_names))
        

#------------------------------------------------------------------------------

def update(d, key, items):
    if key in d.keys():
        d[key].update(items)
    return d

###############################################################################
### DataContainer

class MetaDataContainer:
    """
    
    """
    def __init__(self, meta_dict):
        """
        Parameters
        ----------
        meta_dict       :   dict
            dictionary containing the parameter values from parsing an
            (IN12) ILL ASCII data file
        """
        self.metadata = meta_dict

    def get(self, key):
        """
        Parameters
        ----------
        key             :   str
            key of the querried parameter
        """
        if key in self.metadata.keys():
            return self.metadata[key]
        else:
            for mkey in self.metadata.keys():
                try:
                    return self.metadata[mkey][key]
                except:
                    pass
#                if key in self.metadata[mkey].keys():
#                    return self.metadata[mkey][key]
        return {key : None}

#------------------------------------------------------------------------------

class NeutronDataContainer:
    """
    
    """
    def __init__(self, neutron_data, colnames=None, units=None):
        """
        Parameters
        ----------
        neutron_data    :   ndarray
            array containing the data of a TAS instrument scan
        colnames        :   list
            list of names describing columns in neutron_data
        units           :   list
            list of unit description sting for each name in colnames
        """

        self.neutron_data = neutron_data
        self.colnames = colnames
        self.units = units

    def get(self, idxs=[], colnames=[]):
        """
        Parameters
        ----------
        idx             :   list[int]
            index value(s) specifying the columns of the data to be returned
        colname         :   list[str]
            column name as key specifying the columns of the data to be returned
            
        Note
        ----
        NeutronDataContainer.get() returns everything
        """
        try:
            assert isinstance(idxs, list)
            assert isinstance(colnames, list)
        except AssertionError:
            raise AssertionError(f"idx = {idxs} or colnames = {colnames} is not a list.")
        
        if not (idxs or colnames):
            print("OPTION 1")
            return self.neutron_data, self.colnames, self.units
        
        elif not idxs and colnames:
            print("OPTION 2")
            idxs = [self.colnames.index(cn) for cn in colnames]
            return self.neutron_data[:, idxs], colnames, [self.units[idx] for idx in idxs]

        elif idxs and not colnames:
            print("OPTION 3")
            return self.neutron_data[:, idxs], [self.colnames[idx] for idx in idxs], [self.units[idx] for idx in idxs]

        elif idxs and colnames:
            print("OPTION 4")
            colidxs = [self.colnames.index(cn) for cn in colnames]
            idxs = set(colidxs).union(set(idxs))
            idxs = list(idxs)
            return self.neutron_data[:, idxs], [self.colnames[idx] for idx in idxs], [self.units[idx] for idx in idxs]
        else:
            print("This should not happen!")
            raise ValueError("What the f**k is happening")

###############################################################################
                   
if __name__ == "__main__":
    from pprint import pprint
    in12path = "/home/lbeddric/Documents/Data/IN12data/4-01-1642/data/testfile"
    with open(in12path, "r") as f:
        lines = f.readlines()
    
    in12parser = IN12Parser()
    metadata, ndata = in12parser.parse(in12path)
    
    ### METADATA    
    print(metadata.metadata)
    pprint(metadata.get("PARAM"))

    ### NEUTRONDATA
    print(ndata.get(colnames=[]))


    ### Test individual parser
    # ParameterParser
    pparser = ParamParser()
#    print("ParameterParser: ", pparser.parse(*(lines[40].split(":"))))
    
    # CommandParser
    cparser = CommandParser()
#    print("CommandParser: ", cparser.parse(*(lines[15].split(":"))))

    # PassParser
    passparser = PassParser()
#    print("PassParser: ", passparser.parse(*(lines[27].split(":"))))
    
    # PosQEParser
    posqe = PosQEParser()
#    print("PosQEParser: ", posqe.parse(*(lines[16].split(":"))))
    #Using ParamParser is even better!
#    print("ParamParser: ", pparser.parse(*(lines[16].split(":"))))
    
    # InstrParser
    instrparser = InstrParser()
#    print("InstrumentParser: ", instrparser.parse(*(lines[7].split(":"))))
    
    # FileNrParser
    filenrparser = FileNrParser()
#    print("FileNrParser: ", filenrparser.parse(*(lines[11].split(":"))))

    # DateParser
    dateparser = DateParser()
#    print("Date and Time: ", dateparser.parse(*(lines[12].split(":"))))

#    print("PARAM with ParamParser: ", pparser.parse(*(lines[22].split(":"))))
#    print("ZEROS with ParamParser: ", pparser.parse(*(lines[32].split(":"))))
    
#    data_descr_line = lines[49]
#    print(data_descr_line)
#    read_devices = [dev for dev in data_descr_line.split(" ") if (dev != "" and dev != "\n")]
#    print(read_devices)
#    
#    at_data = False
#    linecounter = 0
#    with open(in12path, "r") as f:
#        # read lines as lon as "DATA_" specifier in file is not reached
#        while not at_data:
#            linecounter += 1
#            line = f.readline()
#            print(line)
#            splitted = line.split(":")
#            key = splitted[0]
#            
#            if key == "DATA_":
#                last_line = f.readline()
#                print("The last LINE!")
#                at_data = True
#        data = genfromtxt(in12path, skip_header=linecounter+1)
#        print(data[0])