#!/usr/bin/env python3

import mechanize as mechanize

br = mechanize.Browser()

"""
WARNING: This is an (almost) one-size fits all script designed to work in
well-behaved cases only. For example, if "Structure Relations" cannot detect
the transformation matrix relating high and low symmetry structures, in its
current form this script will fail. In the future, maybe it could be
generalised to handle such exceptional cases.

For some reason it doesn't like paths to files in different directories.

Run in verbose mode (--v flag if from terminal) to print each step to screen

Example:

python amplimodesfile.py HSfile.cif LSfile.cif > output.html

"""


def scrape_amplimodes(HSfile, LSfile, verbose=False):
    """
    Script for analysing cif files using amplimodes
    Returns the text of an html file of the final page
    """

    # Interacting with Amplimodes website
    response = br.open('http://cryst.ehu.es/cryst/amplimodes.html')

    # Page 1: Select high-sym and low-sym cif files -> click "Calculate..."
    if verbose:
        print('\n\n\nPage 1\n')
        print(response.read().decode('utf-8'))
    br.form = list(br.forms())[1]
    br.form.find_control('cifile1').add_file(open(HSfile),
                                             'text/plain', HSfile)
    br.form.find_control('cifile2').add_file(open(LSfile),
                                             'text/plain', LSfile)
    response = br.submit()

    """
    From here on it gets a bit repetitive but since we're navigating a website
    it makes sense to be explicit.
    """

    # Page 2: Verify BCS representation of cif file -> click "Calculate..."
    if verbose:
        print('\n\n\nPage 2\n')
        print(response.read().decode('utf-8'))
    br.form = list(br.forms())[0]
    response = br.submit()

    # Page 3: Loaded strucs -> click "Find compatable transformation matrices"
    if verbose:
        print('\n\n\nPage 3\n')
        print(response.read().decode('utf-8'))
    br.form = list(br.forms())[0]
    response = br.submit()

    # Page 4: Found Strucutre relations -> click "analyze via amplimodes"
    if verbose:
        print('\n\n\nPage 4\n')
        print(response.read().decode('utf-8'))
    print(list(br.forms()))
    br.form = list(br.forms())[1]
    response = br.submit()
    html = str(response.read().decode('utf-8'))

    # Possible Page 4b (only if structure is polar)
    if ('The distorted structure is polar' in html and
        'Do you want AMPLIMODES to shift the origin?' in html):
        if verbose:
            print('\n\n\nPage 4b (polar structure)\n')
            print(html)
        br.form = list(br.forms())[0]
        response = br.submit()
        html = str(response.read().decode('utf-8'))

    # Page 5: Sym mode analysis -> DON'T HAVE TO click "Detailed information"!
    # (it is not a different page, if you open the html you will have to)
    if verbose:
        print('\n\n\nPage 5\n')

    return html


# If running from terminal  (will need to pipe output html file)
if __name__ == '__main__':
    import sys
    HSfile = str(sys.argv[1])  # First argument is HS .cell file
    LSfile = str(sys.argv[2])  # Second argument is LS .cell file
    if '--v' in sys.argv[3:] or '--verbose' in sys.argv[3:]:
        verbose = True
    else:
        verbose = False
    print(scrape_amplimodes(HSfile, LSfile, verbose))
