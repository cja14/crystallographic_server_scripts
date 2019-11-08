# crystallographic_server_scripts
A collection of python scripts to interface with tools available on crystallographic web servers (Isotropy Software Suite/Bilbao Crystallographic Server).


Requirements:
* python (scripts should work with both versions 2.7 and 3.5)
* the following modules installed: numpy, pandas, ase, mechanize, selenium

There are four main scripts to this repository:

* findsymfile.py -- script to interface with the findsym web app for detecting crystal space group symmetry - part of the Isotropy software suite.
* amplimodesfile.py -- script to interface with the Amplimodes web app for analysing mode amplitudes - part of the Bilbao software suite.
* analyse_amplimodes_html.py -- the amplimodesfile.py script saves output as an html file of the mode amplitudes summary page. This script extracts the amplitude summaries and distortion vectors as _pandas_ dataframes.
* isodistortfile.py -- script for freezing distortions into a parent structure using the the Isodistort web app - part of the Isotropy software suite.

Additionally, _casase.py_ provides a wrapper to load structures using the _ase_ (atomic simulation enviroment) and _iso_index_as.py_ provides a command line script to easily convert a .cif file to a lower symmetry setting. This has been found to be important when comparing the amplitudes of modes from structures with different symmetries using amplimodes.

** It is recommended to familiarise yourself with these scripts that you take a look at the tutorial in the _examples/_ directory.**

