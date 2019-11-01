import pandas as pd

"""
Script to extract table of mode amplitudes and the direction vector of each
mode from an amplimodes output webpage (saved as an html file).

If run from the terminal, output will be printed to stdout:

python analyse_amplimodes_html.py filename.html
"""


def extract_modes(htmlfile, primnorm=False):
    """
    Extract summary table of all irreps (by default with normal amplitudes)
    and a list of the displ. vector for each irrep (in terms of Wyckoff posns)
    returns in pd.DataFrame format
    """
    tables = pd.read_html(htmlfile)

    # Get rid of the comment lines and make first row columns
    for i, tab in enumerate(tables):
        if len(tab) == 1:
            del(tables[i])
        else:
            tab.columns = tab.iloc[0]
            tab = tab[1:]
            tables[i] = tab  # not sure if this is actually necessary
    
    # Table summarising all irreps (note: u'Amplitude (\xc5)' for Amp column)
    sum_idxs = [i for i, _tab in enumerate(tables) if 'K-vector' in _tab]
    if primnorm:
        summary = tables[sum_idxs[1]]
    else:
        summary = tables[sum_idxs[0]]
    
    # Displacement vectors (in terms of Wyckoff posns)
    # This part gets quite hacky
    displ_idxs = [i + sum_idxs[1] + 1 for i, tab in
                  enumerate(tables[sum_idxs[1]+1:])
                  if ('Atom' not in tab and len(tab) == 1)]
    
    # In case the crude screening doesn't work
    if len(displ_idxs) != len(summary):
        if len(displ_idxs) != len(summary)+1:
            print('Houston, we have a problem.')
        while len(displ_idxs) < len(summary):
            displ_idxs += [displ_idxs[0]]
        if len(displ_idxs) > len(summary):
            displ_idxs = displ_idxs[:len(summary)]
        """
        print('\nIrreps:')
        print(summary['Irrep'])
        print('\nDisplacements:')
        for di in displ_idxs:
            print('\nidx = '+str(di))
            print(tables[di])
        """
    displ_tabs = [tables[di] for di in displ_idxs]
    return summary, displ_tabs


# If running from terminal
if __name__ == '__main__':
    import sys
    htmlfile = sys.argv[1]
    args = {}
    if sys.argv[2:]:
        for arg in sys.argv[2:]:
            argsplit = arg.split('=')
            if len(argsplit) == 2:
                args[argsplit[0]] = argsplit[1]
            else:
                break
    summary, displ_tabs = extract_modes(htmlfile, **args)
    print('\nSummary:')
    print(summary)
    for i, dtab in enumerate(displ_tabs):
        print('\n'+str(summary['Irrep'][i+1]))
        print(displ_tabs[i])
