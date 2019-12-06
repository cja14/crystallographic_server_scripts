#!/usr/bin/env python3

import mechanize as mechanize
from casase import casread
br = mechanize.Browser()

"""
Example:

python findsymfile.py structure.cell tol=0.001 > output.cif

"""


def scrape_findsym(filename, origin=2, tol=0.0002, axeso='abc', axesm='ab(c)',
                   index=None, format=None):
    """
    Script for analysing structure files using findsym
    Returns a cif of the high symmetry structure
    """
    # atoms = ase.io.read(filename, index=index, format=format)
    atoms = casread(filename)
    n = len(atoms)
    elems = ' '.join(atoms.get_chemical_symbols())
    cell = atoms.get_cell()
    latvecs = [' '.join([str(c) for c in cell[i, :]])+'\r\n' for i in range(3)]
    posns = atoms.get_scaled_positions()
    positions = [' '.join([str(p) for p in posns[i, :]])+'\r\n'
                 for i in range(n)]
    spins = atoms.get_magnetic_moments()
    print("positions: ", positions)
    print("posns: ", posns)
    print("spins: ", spins)


    # Interacting with findsym websiteb
    br.open('http://stokes.byu.edu/iso/findsym.php')
    br.form = list(br.forms())[1]
    br['title'] = filename
    # br['accuracy'] = str(tol)
    br['acclat'] = str(tol)
    br['accpos'] = str(tol)
    br['axeso'] = [axeso]
    br['axesm'] = [axesm]
    br['vectors'] = ''.join(latvecs)
    br['atoms'] = str(n)
    br['types'] = elems
    br['positions'] = ''.join(positions)
    br['origin'] = [str(origin)]
    response = br.submit()
    cifstart = '# CIF file created by FINDSYM'
    cifend = '# end of cif'
    # output = remove_text_inside_brackets(response.read())
    output = response.read().decode('utf-8')
    return output[output.index(cifstart):output.index(cifend)+len(cifend)]


# If running from terminal (will need to pipe output cif file)
if __name__ == '__main__':
    import sys
    filename = str(sys.argv[1])  # First argument is structure file
    args = {}
    if sys.argv[2:]:
        for arg in sys.argv[2:]:
            argsplit = arg.split('=')
            if len(argsplit) == 2:
                args[argsplit[0]] = argsplit[1]
            else:
                break
    print(scrape_findsym(filename, **args))
