# Before you start

Before starting this tutorial, check that you have the following:

* python installed
* The following python packages installed: numpy, pandas, ase, mechanize, selenium
* An active internet connection


# Findsym - detect space group symmetry of a structure

First we are going to detect the symmetry of a crystal using the findsym functionality from the Isotropy software suite. 

_H. T. Stokes, D. M. Hatch, and B. J. Campbell, FINDSYM, ISOTROPY Software Suite, iso.byu.edu._
_H. T. Stokes and D. M. Hatch, "Program for Identifying the Space Group Symmetry of a Crystal", J. Appl. Cryst. 38, 237-238 (2005)._

In the examples directory you will find several ".cell" files for different Ca3Ti2O7 Ruddlesden-Popper structures. These files are the standard structure format of the CASTEP DFT code. However, since the scripts use ase (atomic simulation environment) to read/write structure files, this example should work just as well with any of the standard atomic structure file formats (".xyz", "POSCAR" etc.). 

There are two ways to run the findsymfile.py script, from the command line and from within python. Let's start from the command line. From within the examples directory, type:

_python ../findsymfile.py Ca3Ti2O7_I4mmm.cell tol=0.001 > Ca3Ti2O7_I4mmm.cif_


# Amplimodes - describe low-symmetry structure in terms of distortions from high-symmetry parent

http://www.cryst.ehu.es/cryst/amplimodes.html



# Isodistort - freeze distortions into a high-symmetry structure

https://stokes.byu.edu/iso/isodistort.php

