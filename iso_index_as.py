#!/usr/bin/python

import os
import sys
from isodistortfile import isodistort

"""
Script for representing a cif file as a lower symmetry space group by
inputing zero amplitude distortions using isodistort

e.g.
./iso_index_as.py input.cif output.cif 31

To make an output file that is space group 31 from input.cif

or ./iso_index_as.py input.cif output.cif 31 2

If you know that the particular SG 31 cell you want is the third option.
"""

HSfile = os.getcwd()+'/'+sys.argv[1]
outputfile = sys.argv[2]
SG = int(sys.argv[3])
if len(sys.argv) > 4:
    list_id = int(sys.argv[4])
else:
    list_id = 0

iso = isodistort(HSfile, silent=True)
iso.choose_by_spacegroup(SG)
iso.select_space_group(list_id=list_id)
iso.set_amplitudes(outputfile, {})
iso.close()
