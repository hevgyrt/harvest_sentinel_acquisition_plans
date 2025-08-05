#!/usr/bin/python
""" Script for harvesting .kml information for Sentinel acquisition-plans
    with the possibility to use an in-house method to filter out polygons
    within our Area of Interest.

	USAGE:
        "python scriptname.py"

	COMMENTS:
		- only works for Sentinel-1 and Sentinel-2 at the moment

===========================================================
Name:          harvest_acquisition_plans.py
Author(s):     Trygve Halsne 22.11.2017 (dd.mm.YYYY)
Modifications: 
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""

import urllib3 as ul
import lxml.etree as ET
from lxml import html
import datetime
import os
import sys
import urllib.request

from extract_entries_S2 import extract_S2_entries # in-house developed method
from extract_entries_S1 import extract_S1_entries

def kml_file_storage_and_extraction(satellite, file_url, output_filename, output_path, extract_area=False):
    """ Store .kml files from url to your output directory.
        Extraction of user defined AOI is optional.
    """
    #print(file_url)
    if not extract_area:
        urllib.request.urlretrieve(file_url, filename=str(output_path + output_filename + '.kml'))
        print("Successful download of %s" % file_url)
        return True
    else:
        urllib.request.urlretrieve(file_url, filename=str(output_path + output_filename + '.kml'))
        if satellite == "Sentinel-1":
            entries = extract_S1_entries(str(output_path + output_filename + '.kml'),
                str(output_filename + '_norwAOI.kml'), output_path)
        elif satellite == "Sentinel-2":
            entries = extract_S2_entries(str(output_path + output_filename + '.kml'),
                str(output_filename + '_norwAOI.kml'), output_path)
        else:
            print("Unknown type of satellite: %s. Only works for 'Sentinel-1' and 'Sentinel-2' at the moment" % satellite)
            return False
        if not entries:
            print("Could not extract entries from AOI for %s" % output_filename)
            return False
        else:
            print("Successful download and retreival of polygons from %s" % file_url)
            return True

#Setting some initial parameters for e.g. harvesting sites and storage path

s1_url = 'https://sentinels.copernicus.eu/en/copernicus/sentinel-1/acquisition-plans/'  
s2_url = 'https://sentinels.copernicus.eu/en/copernicus/sentinel-2/acquisition-plans/'
url_kml_prefix = 'https://sentinels.copernicus.eu'  
storage_path =  str(os.getcwd() + '/')


# Parsing URLs
s1_tree = html.parse(urllib.request.urlopen(s1_url))
s2_tree = html.parse(urllib.request.urlopen(s2_url))

liElementsS1 = []
for tree in [s1_tree]:
    bodyElement = tree.findall('./')[1]
    for li in bodyElement.findall('.//li'):
        liElementsS1.append(li)

liElementsS2A = []
liElementsS2B = []
liElementsS2C = []

for tree in [s2_tree]:
    bodyElement = tree.findall('./')[1]
    for div in bodyElement.find(".//div[@class='sentinel-2a']"):
        for li in div.findall('.//li'):
            liElementsS2A.append(li)
    for div in bodyElement.find(".//div[@class='sentinel-2b']"):
        for li in div.findall('.//li'):
            liElementsS2B.append(li)
    for div in bodyElement.find(".//div[@class='sentinel-2c']"):
        for li in div.findall('.//li'):
            liElementsS2C.append(li) 

# Parse elements following a certain pattern i.e. li-element with href attribute. Text starting with date and whitespace
kml_dictS1 = {}
for li in liElementsS1:
    for c in  li.getchildren():
        if 'href' in c.attrib:
            href = c.attrib['href']
            if href.startswith('/documents'):
                element_text = c.text
                start_text = element_text.split()[0]
                if not element_text.startswith('Sentinel'):
                    if href.endswith('00'):
                        kml_dictS1[href.split('/')[-1]] = str(url_kml_prefix + href)
                    else:
                        for i in range(len(href.split('/'))):
                            if href.split('/')[-i].endswith('kml'):
                                kml_dictS1[href.split('/')[-i]] = str(url_kml_prefix + href)




kml_dictS2A = {}
for li in liElementsS2A:
    for c in  li.getchildren():
        if 'href' in c.attrib:
            href = c.attrib['href']
            if href.startswith('/documents'):
                element_text = c.text
                start_text = element_text.split()[0]
                if not element_text.startswith('Sentinel'):
                    if href.endswith('00'):
                        kml_dictS2A[href.split('/')[-1]] = str(url_kml_prefix + href)
                    else:
                        for i in range(len(href.split('/'))):
                            if href.split('/')[-i].endswith('kml'):
                                kml_dictS2A[href.split('/')[-i]] = str(url_kml_prefix + href)



kml_dictS2B = {}
for li in liElementsS2B:
    for c in  li.getchildren():
        if 'href' in c.attrib:
            href = c.attrib['href']
            if href.startswith('/documents'):
                element_text = c.text
                start_text = element_text.split()[0]
                if not element_text.startswith('Sentinel'):
                    if href.endswith('00'):
                        kml_dictS2B[href.split('/')[-1]] = str(url_kml_prefix + href)
                    else:
                        for i in range(len(href.split('/'))):
                            if href.split('/')[-i].endswith('kml'):
                                kml_dictS2B[href.split('/')[-i]] = str(url_kml_prefix + href)

kml_dictS2C = {}
for li in liElementsS2C:
    for c in  li.getchildren():
        if 'href' in c.attrib:
            href = c.attrib['href']
            if href.startswith('/documents'):
                element_text = c.text
                start_text = element_text.split()[0]
                if not element_text.startswith('Sentinel'):
                    if href.endswith('00'):
                        kml_dictS2C[href.split('/')[-1]] = str(url_kml_prefix + href)
                    else:
                        for i in range(len(href.split('/'))):
                            if href.split('/')[-i].endswith('kml'):
                                kml_dictS2C[href.split('/')[-i]] = str(url_kml_prefix + href)

# Parse filenames to find latest file for each satellite. Also check that "today" is within start and end date
dateformat = '%Y%m%dT%H%M%S'

S1A_key = None
#S1B_key = None 
S1C_key = None #adding c
S2A_key = None
S2B_key = None
S2C_key = None #adding c



for key in list(kml_dictS1.keys()):

    # Parse date formats
    splitted_fname = key.split('_')
    if not (len(splitted_fname)>1):
        splitted_fname = key.split('-')

    end_date = datetime.datetime.strptime(splitted_fname[-1].split('.')[0],dateformat)
    start_date = datetime.datetime.strptime(splitted_fname[-2],dateformat)
    today =  datetime.datetime.now()
    if start_date < today < end_date:
        if (key.startswith('Sentinel-1A') or key.startswith('s1a')):
            if S1A_key:
                # If you have multiple files covering today's date, choose the one with latest end_date
                this_end_date = datetime.datetime.strptime(S1A_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S1A_key = key
            else:
                S1A_key = key

        elif (key.startswith('Sentinel-1C') or key.startswith('s1c')): #adding for C
            if S1C_key:
                this_end_date = datetime.datetime.strptime(S1C_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S1C_key = key
            else:
                S1C_key = key

        """        
        elif (key.startswith('Sentinel-1B') or key.startswith('s1b')):
            if S1B_key:
                this_end_date = datetime.datetime.strptime(S1B_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S1B_key = key
            else:
                S1B_key = key
        """



for key in list(kml_dictS2A.keys()):

    #MP_ACQ__KML Parse date formats
    splitted_fname = key.split('_')
    if not (len(splitted_fname)>1):
        splitted_fname = key.split('-')

    end_date = datetime.datetime.strptime(splitted_fname[-1].split('.')[0],dateformat)
    start_date = datetime.datetime.strptime(splitted_fname[-2],dateformat)
    today =  datetime.datetime.now()
    
    if start_date < today < end_date:
        if (key.startswith('s2a')):
            if S2A_key:
                this_end_date = datetime.datetime.strptime(S2A_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S2A_key = key
            else:
                S2A_key = key

for key in list(kml_dictS2B.keys()):

    # Parse date formats
    splitted_fname = key.split('_')
    if not (len(splitted_fname)>1):
        splitted_fname = key.split('-')

    end_date = datetime.datetime.strptime(splitted_fname[-1].split('.')[0],dateformat)
    start_date = datetime.datetime.strptime(splitted_fname[-2],dateformat)
    today =  datetime.datetime.now()

    if start_date < today < end_date:
        if (key.startswith('s2b')):
            if S2B_key:
                this_end_date = datetime.datetime.strptime(S2B_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S2B_key = key
            else:
                S2B_key = key

for key in list(kml_dictS2C.keys()):  #adding for c

    # Parse date formats
    splitted_fname = key.split('_')
    if not (len(splitted_fname)>1):
        splitted_fname = key.split('-')

    end_date = datetime.datetime.strptime(splitted_fname[-1].split('.')[0],dateformat)
    start_date = datetime.datetime.strptime(splitted_fname[-2],dateformat)
    today =  datetime.datetime.now()

    if start_date < today < end_date:
        if (key.startswith('s2c')):
            if S2C_key:
                this_end_date = datetime.datetime.strptime(S2C_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S2C_key = key
            else:
                S2C_key = key



# Store original .kml files and extract values



if S1A_key:
    s1a_OK = kml_file_storage_and_extraction(satellite='Sentinel-1',file_url=kml_dictS1[S1A_key], output_filename='S1A_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-1A")
    s1a_OK = False

"""
if S1B_key:
    s1b_OK = kml_file_storage_and_extraction(satellite='Sentinel-1',file_url=kml_dictS1[S1B_key], output_filename='S1B_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-1B")
    s1b_OK = False
"""

if S1C_key: #adding for c
    s1c_OK = kml_file_storage_and_extraction(satellite='Sentinel-1',file_url=kml_dictS1[S1C_key], output_filename='S1C_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-1C")
    s1c_OK = False

if S2A_key:
    s2a_OK = kml_file_storage_and_extraction(satellite='Sentinel-2',file_url=kml_dictS2A[S2A_key], output_filename='S2A_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-2A")
    s2a_OK = False

if S2B_key:
    s2b_OK = kml_file_storage_and_extraction(satellite='Sentinel-2',file_url=kml_dictS2B[S2B_key], output_filename='S2B_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-2B")
    s2b_OK = False

if S2C_key: #adding for c
    s2c_OK = kml_file_storage_and_extraction(satellite='Sentinel-2',file_url=kml_dictS2C[S2C_key], output_filename='S2C_acquisition_plan', output_path=storage_path, extract_area=True)
else:
    print("Could not retreive data for Sentinel-2C")
    s2c_OK = False


if not (s1a_OK and s1c_OK and s2a_OK and s2b_OK and s2c_OK):
    print("\nFailed to download all. See comments above.")
else:
    print("\nAll downloads and operations completed successfully.")

