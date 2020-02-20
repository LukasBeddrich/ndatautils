# ndatautils
The ndatautlis package provides utilities for handling neutron scattering
data files acquired on instruments, controlled by the NICOS software, at
the Research Neutron Source Heinz-Maier Leibnitz (FRM II).

ndatautils was brought to life by the necessity of parsing the metadata contained
in the dreadful '.tof' and '.pad' files as produced by NICOS fom CASCADE
detector data. The package is meant to be used as a library in short data
evaluation scripts or jupyter notebooks.

The parser does not reverse enginieer the file writing routine of NICOS.

## Requirements
python 3.7<br/>
numpy<br/>
matplotlib<br/>
lmfit<br/>

## <font color="red"> Critical information </font>
This project is in a very experimental stage and probably prematurely uploaded to github (verision = 0.1.0)

## TO-DO's
- change 'tests' to pytest compatible versions
- add ReductionStructure
- add phase adjustment within a ROI (code from Pablo)