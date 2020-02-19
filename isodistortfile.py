# -*- coding: utf-8 -*-
import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

"""
After installing selenium package, I had to download geckodriver from:
https://github.com/mozilla/geckodriver/releases
and then add the directory where I had saved the geckodriver file to my path
"""


class isodistort:
    """ Class for the object that will communicate with isodistort """

    def __init__(self, HSfile, silent=False):
        """ Initialise the isodistort object (open connection and load cif) """
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
        self.driver.implicitly_wait(30)

        # Initial page (load structure)
        base_url = "http://stokes.byu.edu/iso/isodistort.php"
        self.driver.get(base_url)
        self.driver.find_element_by_name("toProcess").clear()
        self.driver.find_element_by_name("toProcess").send_keys(HSfile)
        self.driver.find_element_by_css_selector(
            "input.btn.btn-primary").click()
        self.basetab = self.driver.window_handles[0]
        self.amplitudestab = None
        self.modelabels = None
        self.modenames = None
        self.SGtab = None

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
        """ Select child by spacegroup not by irrep """
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

        self.modelabels = None
        self.modenames = None

        # Changing tabs again
        self.amplitudestab = self.driver.window_handles[-1]

    def switch_tab(self, tab, name=''):
        """ Switch between selenium tabs (usually class attributes) """
        if tab is not None:
            self.driver.switch_to_window(tab)
        else:
            raise ValueError('Cannot switch to ' + name +
                             ' tab when it does not exist.')

    def get_mode_labels(self):
        """
        Once the space group has been selected, save the mode labels
        and the index of each amplitude cell on the form (used internally)
        as class attributes
        """
        self.switch_tab(self.amplitudestab, 'amplitudes')
        time.sleep(5)

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
            else:
                irrep = lnsplt[0].split(']')[1]
                self.modenames[irrep] = []
                self.modelabels[irrep] = []

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

    def set_amplitudes(self, outputfile, amplitudes):
        """
        Once the space group has been selected, distort the parent structure
        and download the child cif.

        input outputfile: filename of the child structure cif
        input amplitudes: dict of form {'irrep_label': [distortion_vect], ...}
        """

        self.switch_tab(self.amplitudestab, 'amplitudes')
        
        if self.modelabels is None:
            self.get_mode_labels()
        
        # Now to actually assign the amplitude values
        for irrep in amplitudes:
            dispvec = amplitudes[irrep]
            elemnames = self.modenames[irrep]
            for i, name in enumerate(elemnames):
                try:
                    elem = self.driver.find_element_by_name(name)
                    elem.clear()
                    elem.send_keys(str(dispvec[i]))
                except NoSuchElementException:
                    import pdb
                    pdb.set_trace()
            
        self.driver.find_element_by_xpath(
            "(//input[@name='origintype'])[3]").click()
        self.driver.find_element_by_css_selector(
            "input.btn.btn-primary").click()
        
        # Changing tabs again
        self.driver.switch_to_window(self.amplitudestab)
        time.sleep(5)
        os.system('mv subgroup_cif.txt '+outputfile)
    
    def close(self):
        """ Close the instance of isodistort class """
        time.sleep(5)
        self.driver.quit()
