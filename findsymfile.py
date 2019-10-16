#!/usr/bin/python

import mechanize as mechanize
import ase.io
br = mechanize.Browser()

"""
Example:

python findsymfile.py structure.cell tol=0.001 > output.cif

"""


def remove_text_inside_brackets(text, brackets="()[]"):
    """
    Stolen unashamedly from:
    http://stackoverflow.com/questions/14596884/remove-text-between-and-in-python
    """
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0
                break
        else:  # character is not a bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)


def scrape_findsym(filename, origin=2, tol=0.0002, axeso='abc', axesm='ab(c)',
                   index=None, format=None):
    """
    Script for analysing structure files using findsym
    Returns a cif of the high symmetry structure
    """
    # atoms = ase.io.read(filename, index=index, format=format)
    atoms = ase.io.read(filename)
    n = len(atoms)
    elems = ' '.join(atoms.get_chemical_symbols())
    cell = atoms.get_cell()
    latvecs = [' '.join([str(c) for c in cell[i, :]])+'\r\n' for i in range(3)]
    posns = atoms.get_scaled_positions()
    positions = [' '.join([str(p) for p in posns[i, :]])+'\r\n'
                 for i in range(n)]

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
    output = remove_text_inside_brackets(response.read())
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
