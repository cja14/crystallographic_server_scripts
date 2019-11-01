# Before you start

Before starting this tutorial, check that you have the following:

* python installed
* The following python packages installed: numpy, pandas, ase, mechanize, selenium
* An active internet connection

Throughout this tutorial, it is assumed that all of the scripts in the crystallographic_server_scripts repository are included in your python path.



# Findsym - detect space group symmetry of a structure

First we are going to detect the symmetry of a crystal using the findsym functionality from the Isotropy software suite. 

https://stokes.byu.edu/iso/findsym.php

_H. T. Stokes, D. M. Hatch, and B. J. Campbell, FINDSYM, ISOTROPY Software Suite, iso.byu.edu._

_H. T. Stokes and D. M. Hatch, "Program for Identifying the Space Group Symmetry of a Crystal", J. Appl. Cryst. 38, 237-238 (2005)._

In the examples directory you will find several ".cell" files for different Ca3Ti2O7 Ruddlesden-Popper structures. These files are the standard structure format of the CASTEP DFT code, open this file with a text editor and you will that it is just a list of fractional positions of 24 atoms within periodically repeating unit cell. To view this structure, try opening it in your favourite crystallographic visualisation software (e.g. jmol, vesta, etc.). Since the scripts use ase (atomic simulation environment) to read/write structure files, this example should work just as well with any of the standard atomic structure file formats (e.g. ".xyz", "POSCAR" etc.).

There are two ways to run the _findsymfile.py_ script, from the command line and from within python. Let's start from the command line. From within the examples directory, type:

``` bash
python ../findsymfile.py Ca3Ti2O7_I4mmm.cell tol=0.001 > Ca3Ti2O7_I4mmm.cif
```

By running the above command, we have run the script _findsymfile.py_ on the file  _Ca3Ti2O7_I4mmm.cell_. This script extracts the atomic structure from the file and inputs it into the findsym website (with the optional parameter "tolerance" set to 0.001). We have then redirected the output to the file _Ca3Ti2O7_I4mmm.cif_. Inspect this output file and you will see that our 24 atom input structure is of the _I4/mmm_ space group (space group 139) and has 6 Wyckoff sites and obeys 32 symmetry operations.

This same operation may also be performed from within python. Again from within the examples directory, open python and type the following two commands:

```python
from findsymfile import scrape_findsym
ciffile = scrape_findsym('Ca3Ti2O7_I4mmm.cell', tol=0.001)
open('Ca3Ti2O7_I4mmm_2.cif').write(ciffile)
```

This should have created a file _Ca3Ti2O7_I4mmm_2.cif_ that is identical to _Ca3Ti2O7_I4mmm.cif_. 

Repeat the above procedure on the _Ca3Ti2O7_Amam.cell_ and _Ca3Ti2O7_A21am.cell_ structures to create cif files names _Ca3Ti2O7_Amam.cif_ and _Ca3Ti2O7_A21am.cif_.



# Amplimodes - describe a low-symmetry structure in terms of distortions from a high-symmetry parent

Now that we have created cif files and found the space group symmetries of all structures, we are going to use amplimodes, from the Bilbao crystallographic server, to describe our low-symmetry structures as distortions of our high-symmetry structure.

http://www.cryst.ehu.es/cryst/amplimodes.html

_D. Orobengoa, C. Capillas, M.I. Aroyo & J.M. Perez-Mato J. Appl. Cryst. (2009) 42, 820-833._

_J.M. Perez-Mato, D. Orobengoa and M.I. Aroyo. "Mode Crystallography of distorted structures". Acta Cryst A (2010) 66 558-590_

Let us first describe the Amam structure in terms of distortions of the parent I4/mmm phase. As before, there are two ways of automating interactions with amplimodes. From a command line, type the following:

"""bash
python amplimodesfile.py Ca3Ti2O7_I4mmm.cif Ca3Ti2O7_Amam.cif > Ca3Ti2O7_Amam_amplimodes.html
"""

This will automatically click through all the steps on the amplimodes website and save a copy of the final page of the process as an .html file. Try opening this file using your favourite browser to inspect the output.

The function associated with this script can also be imported and used within python. By inspecting the script see if you can do this to analyse the modes of the file _Ca3Ti2O7_A21am.cif_ .

To automate extraction of important data from these html files, I have written another script _analyse_amplimodes_html.py_. Let's perform this next step from within python. Open python and type the following lines:

"""python
from analyse_amplimodes_html import extract_modes
htmlfile = 'Ca3Ti2O7_Amam_amplimodes.html'
summary, displ_tabs = extract_modes(htmlfile)
"""

You now have two objects, _summary_ and _displ_tabs_ . The former is a pandas dataframe that gives a summary of the amplitudes and irrep of each distortion. The latter is a list of dataframes corresponding to each of the irreps. Each dataframe gives the displacement vector associated with each irrep.



# Isodistort - freeze distortions into a high-symmetry structure

In the previous exercise, we had the high and low-symmetry crystal structures and we used amplimodes to find the distortions that relate these phases. In this exercise we are going to approach the problem from the other direction: we will use isodistort to freeze distortions into our high-symmetry phase and create a low-symmetry child structure.

https://stokes.byu.edu/iso/isodistort.php

