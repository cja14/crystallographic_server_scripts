#!/usr/bin/env python3
"""
This module contains functions that interpolate between two low-symmetry
structures relative to a high-symmetry structure.
"""
from glob import glob
from isodistortfile import isodistort
import os
import fileinput
from ase.io import read, write
from ase.spacegroup import get_spacegroup
import time
import numpy as np

class StructureInterp:
    """
    Class for the interpolation between two low-symmetry structures with
    different order parameters relative to a high-symmetry structure.
    """

    def __init__(self, HSfile, LS1file, LS2file, subgroup, silent=True):
        self.HS = HSfile
        self.LS1 = LS1file
        self.LS2 = LS2file
        self.LS1sub = self.LS1.replace(".cif", "_" + str(subgroup) + ".cif")
        self.LS2sub = self.LS2.replace(".cif", "_" + str(subgroup) + ".cif")
        self.subgroup = subgroup
        self.silent = silent
        self.modeValues = None
        self.interpList = []

    def reduce_common_subgroup(self):
        """
        This function reduces the two low-symmetry files to a common subgroup
        with common lattice parameters.

        Parameters:
        ----------
        subgroup: int
            The number corresponding to the space group of the common subgroup
            to both low-symmetry structures.

        cellparams: int
            The lattice parameters to use for the common reduction of both
            low-symmetry structures. 0: high-symmetry file, 1: low-symmetry
            file 1, 2: low-symmetry file 2.

        Returns:
        --------
        LS#file_"subgroup".cif: file
            Two CIF files in the same directory for the two reduced structures

        THIS DOES NOT WORK.
        """

        for iLs, sfile in [self.LS1, self.LS2]:
            #Initialise ISODISTORT and get reduced structure
            iso = isodistort(sfile, silent=self.silent)
            iso.choose_by_spacegroup(self.subgroup)
            iso.select_space_group()

            #Save CIF file and get new name
            flist[iLs] = sfile.replace(".cif", "_" + str(self.subgroup) + ".cif")
            iso.saveCif(fname=flist[iLs], close=True)

    def get_extremal_mode_vectors(self):
        """
        This function gets the values of the displacements of the irreducible
        sites of the structures between which we are interpolating.
        """
        if self.modeValues is not None:
            print("Extremal modes have already been extracted.")
            return None

        #Initialise Isodistort instance with HTT
        iso = isodistort(self.HS, silent=self.silent)

        self.modeValues = []

        for lsFile in [self.LS1sub, self.LS2sub]:
            iso.load_lowsym_structure(lsFile)
            iso.get_mode_labels()
            self.modeValues.append(iso.modevalues)

        return self.modeValues

    def get_interp_modevalues(self, mode, theta=45.0, dtheta=1.5):
        """
        This function interpolates between the values of the chosen mode.

        Parameters:
        -----------
        mode: str
            The name of the mode whose values are to be interpolated. Note that
            this mode must be present in both end structures.

        theta: float
            The range of "angles" to be considered.

        dtheta: float
            The spacing between the angles of the order parameter for the
            interpolation.
        """

        #Convert to radians
        theta = theta*np.pi/180
        dtheta = dtheta * np.pi / 180
        tvals = np.arange(dtheta, theta, dtheta)

        #Get mode values if None
        if self.modeValues is None:
            _ = self.get_extremal_mode_vectors()

        #Get initial and final order parameter vector
        initial = self.modeValues[0][mode]
        final = self.modeValues[1][mode]
        print("Initial vector:", initial)
        print("Final vector:", final)

        #Get scale factor
        delta = [np.sqrt(2)*final[k]/initial[k] - 1 for k in\
                range(0,len(initial), 2)]

        for t in tvals:
            #Get vector of values
            itpList = [0 for i in range(len(initial))]
            itpList[::2] = [even*(np.cos(t) + delta[i]*np.sin(t)) for i, even\
                    in enumerate(initial[::2])]
            itpList[1::2] = [even*(np.sin(t) + delta[i]*np.sin(t)*np.tan(t)) \
                    for i, even in enumerate(initial[::2])]
            #Extract initial dictionary and set the mode values to interpolated
            #values
            itpDict = self.modeValues[0].copy()
            itpDict[mode] = itpList
            self.interpList.append(itpDict)

        return self.interpList

    def print_interp_cif(self):

        itp = isodistort(self.HS)
        itp.load_lowsym_structure(self.LS1sub)
        
        for i, amps in enumerate(self.interpList):
            itp.modevalues = amps
            itp.set_amplitudes
            itp.saveCif(fname="interpolated_" + str(i) + ".cif")
            count=0
            while "subgroup_cif.txt" in os.listdir('.'):
                time.sleep(1)
                count+=1
                assert count < 10, "Took too long to print CIF file"










