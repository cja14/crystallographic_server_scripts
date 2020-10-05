#!/usr/bin/env python3

from amplimodesfile import scrape_amplimodes
import collections
from findsymfile import findsym_wrap
from analyse_amplimodes_html import extract_modes
from glob import glob
import os.path
import re
import sys

def gen_cif(tol=1e-3, pure=False, print_cif=True):

    cellfiles = glob("*.cell")
    for file in cellfiles:
        seed = file.replace(".cell", ".cif")
        findsym_wrap(file, print_cif=print_cif, pure=pure, lattol=tol,  postol=tol)

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

def isomodes(LSfile, parent=False):
    """
    This function analyses the HTML output from an ISODISTORT mode analysis
    of a structure whose CIF filename is LSfile and returns a mode
    amplitude dictionary.

    Parameters:
    -----------
    LSfile: str
        Name of the LSfile cif file

    Returns:
    --------
    modeDict: dictionary
        Dictionary containing as keys the modes (strings) and as values a
        list of the mode amplitudes in the son and parent phases (float)

    overallDisp: list
        List of the overall distortions in the son and parent phases (Å).
    """
    #Get .html filename
    LSfile = LSfile.replace(".castep", "_ISOmodes.html")

    with open(LSfile, 'r+') as f:
        fCont = f.readlines()
        #Define region of HTML file with content of interest
        for iLine, line in enumerate(fCont):
            if ("mode" in line) and ("As" in line):
                start = iLine + 1
            elif 'Parent-cell strain mode definitions' in line:
                end = iLine
    try:
        modesInfo = fCont[start:end]
        modeDict = {}

        #Get the amplitudes
        for line in modesInfo:
            if " all" in line:
                modeName = line.split()[0].split("]")[1]
                modeAmps = [float(line.split()[2]), float(line.split()[3])]
                if parent:
                    modeDict[modeName] = modeAmps[1]
                else:
                    modeDict[modeName] = modeAmps[0]

            elif "Overall" in line:
                if parent:
                    overallDisp = float(line.split()[2])
                else:
                    overallDisp = float(line.split()[1])
    except UnboundLocalError:
        print("The ISODISTORT output %s is not complete." % LSfile.replace('.cif',\
                '_ISOmodes.html'))
        modeDict = {}
        overallDisp = None

    return modeDict, overallDisp

def compare_modes(HSfile, useAmplimodes=False, parent=False):
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
    dicts: list of ordered dictionaries.
    """
    #Get all .cif files in current directory and remove HS structure
    files = glob("*.cif")

    dicts = [{}, {}, {}]
    for file in files:
        #Get doping value
        if "Al" in file:
            stoich = float(file[file.find("Al") + len("Al"):file.rfind("O4")]) 
        else:
            stoich = 0.00
        #Get phase
        phase = re.search("O4_(.*).cif", file).group(1)

        #Get mode amplitudes
        if useAmplimodes:
            modes = amplimodes(HSfile, file)
        else:
            modes, _ = isomodes(file, parent=parent)

        if phase == "HTT":
            dicts[0][stoich] = modes
        elif phase == "LTT":
            dicts[1][stoich] = modes
        elif phase == "LTO":
            dicts[2][stoich] = modes
        else:
            raise ValueError("Phase is not HTT, LTT or LTO.")

    #Order dictionaries
    for index, d in enumerate(dicts):
        dicts[index] = collections.OrderedDict(sorted(d.items()))
    #Extract values
    x = list(dicts[1].keys()) #Doping values

    return x, dicts

if __name__ == "__main__":
    #Generate .CIF files
    gen_cif()
