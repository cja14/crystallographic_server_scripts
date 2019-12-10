#!/usr/bin/env python3

from amplimodesfile import scrape_amplimodes
import collections
from findsymfile import scrape_findsym
from analyse_amplimodes_html import extract_modes
from glob import glob
import os.path
import re


def gen_cif():

    cellfiles = glob("*.cell")
    for file in cellfiles:
        seed = file.replace(".cell", "")
        f = open(seed + ".cif", "w+")
        f.write(scrape_findsym(file))
        f.close()


def amplimodes(HSfile, LSfile, verbose=False):
    """
    This function interfaces with the Amplimodes web page on the 
    crystallographic server to extract the amplitude of the distortion
    modes between a high-symmetry and low-symmetry structure. 

    It is crucial that the space group of the structure in the LSfile
    be of a different space group to the high-symmetry structure.

    Parameters:
    -----------
    HS: str
        Filename of high-symmetry structure.

    Returns:
    --------
    modes = [{mode: {doping value: amplitude} for doping values} for modes}]
    """
    seed = LSfile.replace(".cif", "")
    #Get html
    if os.path.isfile(seed + ".html")==False:
        html = scrape_amplimodes(HSfile, LSfile, verbose=verbose)
        f = open(seed + ".html", "w+")
        f.write(html)
        f.close()

    summary, disp_tabs = extract_modes(seed + ".html")
    Nmodes = len(summary) #Number of modes
    modedict = {}
        
    for i in range(Nmodes):
        modedict[summary["Irrep"][i+1]] = summary["Amplitude (Å)"][i+1]

    return modedict

def compare_modes(HSfile):
    """
    This function extracts all the mode amplitudes for all the .cif files
    compared to the single high-symmetry structure given by the HSfile .cif
    file.

    Parameters:
    -----------
    HSfile: str
        The filename of the high-symmetry structure .cif file

    Returns:
    --------
    dicts: list of ordered dictionaries
        A list of 
    """    

    #Get all .cif files in current directory and remove HS structure
    files = glob("*LTT*.cif") + glob("*LTO*.cif")

    dicts = [{}, {}, {}]
    for file in files:
        #Get doping value
        print("Filename: ", file)
        if "Al" in file:
            stoich = float(file[file.find("Al") + len("Al"):file.rfind("O4")]) 
        else:
            stoich = 0.00
        #Get phase
        phase = re.search("O4_(.*).cif", file).group(1)

        #Get mode amplitudes
        modes = amplimodes(HSfile, file)
    
        if phase == "HTT":
            dicts[0][stoich] = modes
        elif phase == "LTT":
            dicts[1][stoich] = modes
        elif phase == "LTO":
            dicts[2][stoich] = modes
        else:
            raise ValueError("Phase is not HTT, LTT or LTO")

    #Order dictionaries
    for index, d in enumerate(dicts):
        dicts[index] = collections.OrderedDict(sorted(d.items()))

    #Extract values
    x = list(dicts[1].keys()) #Doping values
    
    return x, dicts

      

if __name__ == "__main__":
    
    gen_cif()
