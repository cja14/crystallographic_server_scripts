#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
from glob import glob
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from subprocess import call
import fnmatch
"""
After installing selenium package, I had to download geckodriver from:
https://github.com/mozilla/geckodriver/releases
and then add the directory where I had saved the geckodriver file to my path
"""


class isodistort:
    """ Class for the object that will communicate with isodistort """

    def __init__(self, HSfile, silent=True):
        """ Initialise the isodistort object (open connection and load cif) """
        # Add cwd to HSfile name
        HSfdir = os.getcwd() + '/' + HSfile

        # The no fuss script
        options = Options()
        options.headless = silent
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting',
                               False)
        profile.set_preference('browser.download.dir', os.getcwd())
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                               'text/plain, text/html, text/csv')
        self.driver = webdriver.Firefox(firefox_profile=profile,
                                        options=options)
        self.driver.implicitly_wait(10)

        # Initial page (load structure)
        base_url = "https://stokes.byu.edu/iso/isodistort.php"
        self.driver.get(base_url)
        self.driver.find_element_by_name("toProcess").clear()
        self.driver.find_element_by_name("toProcess").send_keys(HSfdir)
        self.driver.find_element_by_css_selector(
            "input.btn.btn-primary").click()
        self.basetab = self.driver.window_handles[0]
        self.amplitudestab = None
        self.modelabels = None
        self.modevalues = None
        self.modenames = None
        self.SGtab = None
        self.MDparamtab = None
        self.MDresultstab = None

    def load_lowsym_structure(self, LSfile, origin=[0, 0, 0], \
            use_robust=False, robust_val=1):
        """
        This function uses Method 4 to load a .cif file corresponding to a
        low-symmetry structure.
        Parameters:
        -----------
        LSfile: str
            Filename of low-symmetry file.
        """

        #Add cwd to LSfile
        LSfdir = os.getcwd() + '/' + LSfile
        LSseed = LSfile.strip(".cif")

        #Switch to basetab
        self.switch_tab(self.basetab)

        #Input the low-symmetry .cif file
        try:
            self.driver.find_element_by_name("toProcess").clear()
        except:
            self.driver.find_element_by_name("toProcess").clear()
        self.driver.find_element_by_name("toProcess").send_keys(LSfdir)
        self.driver.find_element_by_xpath('//FORM[@ACTION="isodistortupload'\
               +'file.php"]/h3/INPUT[@CLASS="btn btn-primary"]').click()

        #Switch to tab with decomposition parameters
        self.MDparamtab = self.driver.window_handles[-1]
        self.switch_tab(self.MDparamtab)

        #Input parameters if not default and submit
        #Default is to choose first suggested basis relating high- and low-sy-
        #-mmetry structures
        basis_options = Select(self.driver.find_element_by_name("basisselect")).\
                options
        basis_options[1].click()

        #Origin
        if origin != [0, 0, 0]:
            self.driver.find_element_by_xpath('//INPUT[@NAME="chooseorigin"' +\
                ' and @VALUE="true"]').click()
            for i, orig in enumerate(origin):
                self.driver.find_element_by_name("origin" + str(i+1)).clear()
                self.driver.find_element_by_name("origin" + str(i+1)).send_keys\
                    (str(origin[i]))

        #Wickoff site-matching method
        if use_robust:
            self.driver.find_element_by_xpath('//INPUT[@NAME="trynearest" and ' + \
                '@VALUE="false"]').click()
            self.driver.find_element_by_name("dmax").clear()
            self.driver.find_element_by_name("dmax").send_keys(str(robust_val))

        #Submit
        self.driver.find_element_by_css_selector("input.btn.btn-primary").click()
        time.sleep(1)
        #Switch tab
        self.amplitudestab = self.driver.window_handles[-1]
        self.switch_tab(self.amplitudestab)

    def save_mode_details(self, LSfile, origin=[0, 0, 0], use_robust=False,
            robust_val=1, parent=True):

        """
        This function compares a low-symmetry structure with the given high-
        symmetry structure and outputs the overall distortion and the mode
        amplotudes. Method 4 of the ISODISTORT webtool is used.

        Parameters:
        -----------
        LSfile: str
            Name of the .cif file of the low-symmetry structure.

        """
        # Load low-symmetry structure and change tabs
        self.load_lowsym_structure(LSfile, origin=origin, use_robust=
                                   use_robust, robust_val=robust_val)

        with open(LSfile.replace('.cif', '_ISOmodes.html'), "w+") as html:
                html.write(self.driver.page_source)
        time.sleep(1)


    def get_mode_amps(self, LSfile, origin=[0, 0, 0], use_robust=False,
            robust_val=1, saveCif=False, saveModeDetails=True, parent=True,
            vectors=False):
        """
        This function compares a low-symmetry structure with the given
        high-symmetry structure and outputs the overall distortion and the mode
        amplitudes. Method 4 of the ISODISTORT web-tool is used.

        Parameters:
        -----------
        LSfile: str
            Name of the .cif file of the low-symmetry structure.

        Returns:
        --------
        modeDict: dictionary
            Dictionary associating to each distortion mode a list of two
            amplitudes: the first normalised to the child structure, the second
            normalised to the parent structure.

        overallDisps: list (2)
            List of the two overall distortions from HS to LS normalised
            relative to the HS and LS cells, respectively.
        """
        #Load low-symmetry structure and change tabs
        self.load_lowsym_structure(LSfile, origin=origin, use_robust=\
                use_robust, robust_val=robust_val)

        #Saving files if requested
        if saveCif:
            self.driver.find_element_by_xpath('//INPUT[@VALUE="structurefile"]').\
                    click()
            self.driver.find_element_by_css_selector("input.btn.btn-primary").\
                    click()

        #Get modes and amplitudes
        #Change to window with modes details
        self.driver.find_element_by_xpath('//INPUT[@VALUE="modesdetails"]').\
                click()
        self.driver.find_element_by_css_selector("input.btn.btn-primary").\
                click()
        self.MDresultstab = self.driver.window_handles[-1]
        self.switch_tab(self.MDresultstab)
        time.sleep(2)

        # Save mode details page as a .html file
        if saveModeDetails:
            LSseed = LSfile.strip(".cif")
            with open(LSseed + '_ISOmodes.html', "w+") as html:
                html.write(self.driver.page_source)
            time.sleep(1)


        # Initialise mode dictionary
        modeDict = {}    # Just amplitudes
        modeVecDict = {}  # Order parameter vector
        modesInfo = self.driver.find_element_by_xpath('//div[@class="pad"]/pre')\
            .text.split('Parent-cell strain mode definitions\n')[0]\
            .split('Displacive mode amplitudes\n')[-1]
        #print(modesInfo)
            #.\
            #split('Parent-cell strain mode definitions\n')[0].splitlines()

        # Iterate through mode amplitude region
        for _, line in enumerate(modesInfo):
            if len(line) == 1:
                continue
            if (line != "") and (" all" not in line) and ("Overall" not in
                                                          line)\
            and ("mode" not in line):
                print("Line is: ", line)
                # Define mode name
                modeName = line.split()[0].split("]")[1].split('[')[0]
                # Extract parent or child component of mode vector
                if parent:
                    component = float(line.split()[3])
                else:
                    component = float(line.split()[2])
                # Append to mode vector
                if modeName not in modeVecDict:
                    modeVecDict[modeName] = [component]
                else:
                    modeVecDict[modeName].append(component)

            if " all" in line:
                modeName = line.split()[0].split("]")[1]
                if parent:
                    modeDict[modeName] = float(line.split()[3])
                else:
                    modeDict[modeName] = float(line.split()[2])
            elif "Overall" in line:
                overallDisps = [float(line.split()[1]), float(line.split()[2])]

        if vectors:
            return modeDict, overallDisps, modeVecDict
        else:
            return modeDict, overallDisps

    @staticmethod
    def get_kpoints(irreps):
        """ Extract list of kpoint letters from list of irreps """
        kpoints = {}
        for irrep in irreps:
            i = 1
            while irrep[i].isupper():
                i += 1
            kpoints[irrep] = irrep[:i]
        return kpoints

    def choose_by_irreps(self, irreps):
        """ Load the distortion irreps to isodistort """
        self.switch_tab(self.basetab, 'base')
        kpoints = self.get_kpoints(irreps)

        # Choose number of irreps
        Nirreps = len(irreps)
        if Nirreps > 1:
            elem = self.driver.find_element_by_xpath(\
                "(//input[@name='irrepcount'])[3]")
            elem.clear()
            elem.send_keys(str(Nirreps))
            self.driver.find_element_by_xpath(\
                "(//input[@value='Change'])[2]").click()

        # Select kpoints
        for i, irrep in enumerate(irreps):
            kpt = kpoints[irrep]
            name = "kvec"+str(i+1)
            elem = Select(self.driver.find_element_by_name(name))
            options = elem.options
            for j, opt in enumerate(options):
                if opt.text[:len(kpt)] == kpt:
                    opt.click()
                    break

        self.driver.find_element_by_xpath("(//input[@value='OK'])[2]").click()

        # Control the tabs
        self.SGtab = self.driver.window_handles[-1]
        self.driver.switch_to_window(self.SGtab)

        # Choose irreps
        for i, irrep in enumerate(irreps):
            name = "irrep"+str(i+1)
            elem = Select(self.driver.find_element_by_name(name))
            options = elem.options
            for j, opt in enumerate(options):
                if opt.text[:len(irrep)] == irrep:
                    opt.click()
                    break

        elems = self.driver.find_elements_by_css_selector(
            "input.btn.btn-primary")
        elems[0].click()

        # Changing tabs again
        #self.amplitudestab = self.driver.window_handles[-1]

    def choose_by_spacegroup(self, SG, id_from_list=0):
        """
        This function uses Method 1 to select by spacegroup.

        Parameters:
        ----------
        SG: int
            Space group number of subgroup.

        id_from_list: int
        """
        self.switch_tab(self.basetab, 'base')

        # Select target child space group from list
        elem = Select(self.driver.find_element_by_name("subgroupsym"))
        options = elem.options
        opt = options[int(SG)]  # 0 is "Not selected"
        opt.click()

        elems = self.driver.find_elements_by_css_selector(
            "input.btn.btn-primary")
        elems[4].click()

        # Control the tabs
        self.SGtab = self.driver.window_handles[-1]
        self.driver.switch_to_window(self.SGtab)

    def view_space_groups(self):
        """ Once the irreps have been loaded, view list of space groups """
        self.switch_tab(self.SGtab, 'spacegroup')

        elems = self.driver.find_elements_by_name("orderparam")
        for i, elem in enumerate(elems):
            value = elem.get_property('value')
            print(str(i)+'\t'+str(value))

    def select_space_group(self, SG=None, list_id=0):
        """ Once the irreps have been loaded, select space group by number """
        self.switch_tab(self.SGtab, 'spacegroup')

        # Choose the space group of the final structure
        elems = self.driver.find_elements_by_name("orderparam")
        if SG is not None:
            for i, elem in enumerate(elems):
                value = elem.get_property('value')
                if int(value.split()[1]) == SG:
                    break
        else:
            elem = elems[list_id]
        elem.click()

        self.driver.find_element_by_css_selector(
            "input.btn.btn-primary").click()

        # Changing tabs again
        self.amplitudestab = self.driver.window_handles[-1]
        self.switch_tab(self.amplitudestab)

    def switch_tab(self, tab, name=''):
        """ Switch between selenium tabs (usually class attributes) """
        if tab is not None:
            self.driver.switch_to.window(tab)
        else:
            raise ValueError('Cannot switch to ' + name +
                             ' tab when it does not exist.')

    def get_mode_labels(self):
        """
        This function extracts the mode names, labels and values and stores
        them as internal class attributes.
        """
        self.switch_tab(self.amplitudestab, 'amplitudes')
        time.sleep(1)

        page = self.driver.page_source
        pagelines = page.split('\n')

        for i, ln in enumerate(pagelines):
            if 'Enter mode and strain amplitudes' in ln:
                startln = i + 3
            elif 'Zero all mode and strain amplitudes for all output' in ln:
                endln = i
                break

        # Annoyingly, the modenames are not ordered as one might expect
        self.modelabels = {}
        self.modenames = {}
        self.modevalues = {}
        for i, ln in enumerate(pagelines[startln:endln]):
            lnsplt = ln.split()
            if lnsplt[0] == '</p><p>':
                pass
            elif lnsplt[0] == '<input':
                #irrep = lnsplt[0].split(']')[1]
                for term in lnsplt:
                    if 'name' in term:
                        self.modenames[irrep] += [term[6:-1]]
                    elif 'size' in term:
                        self.modelabels[irrep] += [term[9:-4]]
                    elif 'value' in term:
                        self.modevalues[irrep] += [float(term[7:-1])]
            else:
                irrep = lnsplt[0].split(']')[1]
                self.modenames[irrep] = []
                self.modelabels[irrep] = []
                self.modevalues[irrep] = []

    def view_modes(self):
        """
        Once the space group has been selected, get the distortion vector
        for each irrep.

        returns: dict of form {'irrep_label': [distortion_labels], ...}
        """
        self.switch_tab(self.amplitudestab, 'amplitudes')

        if self.modelabels is None:
            self.get_mode_labels()

        return self.modelabels

    def set_amplitudes(self):
        """
        Once the space group has been selected, distort the parent structure
        and download the child cif.

        Parameters:
        -----------
        """
        # Switch to amplitudes tab
        self.switch_tab(self.amplitudestab, 'amplitudes')

        assert self.modelabels is not None, "Need to get mode labels first."

        # Now to actually assign the amplitude values
        for irrep in self.modevalues:
            dispvec = self.modevalues[irrep]
            elemnames = self.modenames[irrep]
            for i, name in enumerate(elemnames):
                try:
                    elem = self.driver.find_element_by_name(name)
                    elem.clear()
                    elem.send_keys('{:.8f}'.format(dispvec[i]))
                except NoSuchElementException:
                    import pdb
                    pdb.set_trace()

        return None

    def save_cif(self, fname="", close=False):
        """
        This function saves a CIF file of the structure that has been created.
        If  fname is not given, the default ISODISTORT filename will be used.
        It is assumed that the tab the driver is pointed towards is the final
        tab with the amplitudes.
        """
        if fname != "":
            assert ".cif" in fname, "Filename does not end by .cif"
            assert 'subgroup_cif.txt' not in os.listdir("."), \
                    "Already a 'subgroup_cif.txt' file in current directory."
            assert len(fnmatch.filter(os.listdir('.'),
                       'subgroup_cif\(?\).txt')) == 0, "subgroup_cif(?).txt" +\
                "present."

            # Save CIF file (default 'subgroup_cif.txt' filename will be used)
            self.driver.find_element_by_xpath('//INPUT[@VALUE="structurefile"]'
                                              ).click()
            self.driver.find_element_by_css_selector("input.btn.btn-primary").\
                click()
            time.sleep(2)

            # Wait until filename is in current directory
            count = 0
            while 'subgroup_cif.txt' not in os.listdir('.'):
                time.sleep(1)
                count += 1
                assert count < 5, "Took too long to print subgroup_cif.txt"

            # Ensure file is not empty
            count = 0
            while os.path.getsize('subgroup_cif.txt') == 0:
                print("File {} is empty.\n Will delete and try again".format
                      ('subgroup_cif.txt'))
                # Re-download subgroup_cif.txt
                self.driver.find_element_by_css_selector(
                        "input.btn.btn-primary").click()
                time.sleep(1)
                count += 1
                assert count < 5, "Too many empty file instances."

            # Change filename to desired name
            count = 0
            while 'subgroup_cif.txt' in os.listdir('.'):
                call(['mv', 'subgroup_cif.txt', fname])
                time.sleep(1)
                count += 1
                assert count < 5

        else:
            self.driver.find_element_by_xpath('//INPUT[@VALUE="structurefile"]').\
                click()
            self.driver.find_element_by_css_selector("input.btn.btn-primary").\
                click()

        if close:
            self.close()

    def close(self):
        """ Close the instance of isodistort class """
        call(['rm', 'geckodriver.log'])
        self.driver.quit()

if __name__ == "__main__":
    import sys
    #Getting input high- and low-symmetry .cif filenames
    HSfile = str(sys.argv[1])

    #Getting argument dictionary for the get_mode_amps function
    kwargs = {}
    if sys.argv[2:]:
        for arg in sys.argv[2:]:
            argsplit = arg.split('=')
            if len(argsplit) == 2:
                if argsplit[1] == "True":
                    argsplit[1] = True
                elif argsplit[1] == "False":
                    argsplit[1] = False
                kwargs[argsplit[0]] = argsplit[1]
            else:
                break

    #Initialise ISODISTORT class instance 
    iso = isodistort(HSfile, silent=True)
    os.chdir(os.getcwd())
    LSfiles = glob("*.cif")
    for LSfile in LSfiles:
        print(LSfile)
        LShtml = LSfile.replace(".cif", "_ISOmodes.html")
        if not glob(LShtml):
            print("Not already done: ", LShtml)
            modeDict, overallDisps = iso.get_mode_amps(LSfile, **kwargs)

    iso.close()
    if glob("geckodriver.log"):
        os.remove('geckodriver.log')
