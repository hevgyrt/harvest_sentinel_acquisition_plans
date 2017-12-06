#!usr/bin/python2.7
""" Script for harvesting .kml information for Sentinel-2 acquisition-plans and
    using an in-house method to filter out polygons within our Area of Interest.

	USAGE:
        "python scriptname.py"

	COMMENTS:
		- Only works for Sentinel-2 satellites at the moment. Include Sentinel-1

===========================================================
Name:          harvest_acquisition_plans.py
Author(s):     Trygve Halsne 22.11.2017 (dd.mm.YYYY)
Modifications:
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""

import urllib as ul
import urllib2 as ul2
import lxml.etree as ET
from lxml import html
import datetime
import os
import sys

from extract_entries_S2 import extract_S2_entries
from extract_entries_S1 import extract_S1_entries



# Setting some initial parameters
s1_url = 'https://sentinel.esa.int/web/sentinel/missions/sentinel-1/observation-scenario/acquisition-segments'
s2_url = 'https://sentinel.esa.int/web/sentinel/missions/sentinel-2/acquisition-plans'
url_kml_prefix = 'https://sentinel.esa.int'
storage_path = str(os.getcwd() + '/')

s1_tree = html.parse(ul2.urlopen(s1_url))
s2_tree = html.parse(ul2.urlopen(s2_url))

liElements = []
for tree in [s1_tree, s2_tree]:
    bodyElement = tree.findall('./')[1]
    for li in bodyElement.findall('.//li'):
        liElements.append(li)

# Parse elements following a certain pattern i.e. li-element with href attribute. Text starting with date and whitespace
kml_dict = {}
for li in liElements:
    for c in  li.getchildren():
        if c.attrib.has_key('href'):
            href = c.attrib['href']
            if href.startswith('/documents'):
                element_text = c.text
                start_text = element_text.split()[0]
                if start_text.isdigit():
                    kml_dict[href.split('/')[-1]] = str(url_kml_prefix + href)

# Parse filenames to find latest file for each satellite. Also check that "today" is within start and end date
dateformat = '%Y%m%dT%H%M%S'

S1A_key = None
S1B_key = None
S2A_key = None
S2B_key = None

for key in kml_dict.keys():
    end_date = datetime.datetime.strptime(key.split('_')[-1].split('.')[0],dateformat)
    start_date = datetime.datetime.strptime(key.split('_')[-2],dateformat)
    today =  datetime.datetime.now()
    if start_date < today < end_date:
        if key.startswith('Sentinel-1A'):
            if S1A_key:
                # If you have multiple files covering today's date, choose the one with latest end_date
                this_end_date = datetime.datetime.strptime(S1A_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S1A_key = key
            else:
                S1A_key = key
        elif key.startswith('Sentinel-1B'):
            if S1B_key:
                this_end_date = datetime.datetime.strptime(S1B_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S1B_key = key
            else:
                S1B_key = key
        elif key.startswith('Sentinel-2A'):
            if S2A_key:
                this_end_date = datetime.datetime.strptime(S2A_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S2A_key = key
            else:
                S2A_key = key
        elif key.startswith('Sentinel-2B'):
            if S2B_key:
                this_end_date = datetime.datetime.strptime(S2B_key.split('_')[-1].split('.')[0],dateformat)
                if this_end_date < end_date:
                    S2B_key = key
            else:
                S2B_key = key

#sys.exit([0])

# Store original .kml files to path and extract values
def kml_file_storage_and_extraction(satellite, file_url, output_filename, output_path, extract_area=False):
    if not extract_area:
        ul.urlretrieve(file_url, filename=str(output_path + output_filename + '.kml'))
        print "Successful download of %s" % file_url
        return True
    else:
        ul.urlretrieve(file_url, filename=str(output_path + output_filename + '.kml'))
        if satellite == "Sentinel-1":
            entries = extract_S1_entries(str(output_path + output_filename + '.kml'), str(output_filename + '_norwAOI.kml'), output_path)
        elif satellite == "Sentinel-2":
            entries = extract_S2_entries(str(output_path + output_filename + '.kml'), str(output_filename + '_norwAOI.kml'), output_path)
        else:
            print "Unknown type of satellite: %s. Only works for 'Sentinel-1' and 'Sentinel-2' at the moment" % satellite
            return False
        if not entries:
            print "Could not extract entries from AOI for %s"  %output_filename
            return False
        else:
            print "Successful download and retreival of polygons from %s" % file_url
            return True

s2a_OK = kml_file_storage_and_extraction(satellite='Sentinel-2',file_url=kml_dict[S2A_key], output_filename='S2A_acquisition_plan', output_path=storage_path, extract_area=True)
s2b_OK = kml_file_storage_and_extraction(satellite='Sentinel-2',file_url=kml_dict[S2B_key], output_filename='S2B_acquisition_plan', output_path=storage_path, extract_area=True)
s1a_OK = kml_file_storage_and_extraction(satellite='Sentinel-1',file_url=kml_dict[S1A_key], output_filename='S1A_acquisition_plan', output_path=storage_path, extract_area=True)
s1b_OK = kml_file_storage_and_extraction(satellite='Sentinel-1',file_url=kml_dict[S1B_key], output_filename='S1B_acquisition_plan', output_path=storage_path, extract_area=True)

if not (s2a_OK and s2b_OK and s1a_OK and s1b_OK):
    print "\nFailed to download all. See comments above."
else:
    print "\nAll downloads and operations completed successfully."

'''
try:
    ul.urlretrieve(kml_dict[S1A_key], filename='S1A_acquisition_plan.kml')
    entries_S1A = extract_S2_entries('S2B_acquisition_plan.kml', 'S2B_acquisition_plan_norwAOI.kml', storage_path)
    if not entries_S2B:
		print "Could not extract entries from Norwegian AOI for Sentinel-2B"
    print "Successful download and retreival of polygons from %s" % kml_dict[S2B_key]
except:
    print "Could not retreive %s" % kml_dict[S2B_key]

try:
    ul.urlretrieve(kml_dict[S2A_key], filename='S2A_acquisition_plan.kml')
    entries_S2A = extract_S2_entries('S2A_acquisition_plan.kml', 'S2A_acquisition_plan_norwAOI.kml', storage_path)
    if not entries_S2A:
		print "Could not extract entries from Norwegian AOI for Sentinel-2A"
    print "Successful download and retreival of polygons from %s" % kml_dict[S2A_key]
except:
    print "Could not retreive %s" % kml_dict[S2A_key]

try:
    ul.urlretrieve(kml_dict[S2B_key], filename='S2B_acquisition_plan.kml')
    entries_S2B = extract_S2_entries('S2B_acquisition_plan.kml', 'S2B_acquisition_plan_norwAOI.kml', storage_path)
    if not entries_S2B:
		print "Could not extract entries from Norwegian AOI for Sentinel-2B"
    print "Successful download and retreival of polygons from %s" % kml_dict[S2B_key]
except:
    print "Could not retreive %s" % kml_dict[S2B_key]
'''
"""
S1A_last_date_start = None
S1B_last_date_start = None
S2A_last_date_start = None
S2B_last_date_start = None

# Iterate through all .kml filenames to find the document within our period, i.e. (begin_data < today < end_date)
# Manual iteration not following the KISS principle..
for key in kml_dict.keys():
    if key.startswith('Sentinel-2A'):
        if not S2A_last_date_start:
            S2A_last_date_start =  datetime.datetime.strptime(key.split('_')[-2],dateformat) #from date
            if S2A_last_date_start > datetime.datetime.now():
                S2A_last_date_start = None
                S2A_key = key
            else:
                S2A_key = key

        else:
            S2A_current_date_start = datetime.datetime.strptime(key.split('_')[-2],dateformat)
            S2A_current_date_end = datetime.datetime.strptime(key.split('_')[-1].split('.')[0],dateformat)
            if (S2A_current_date_start > S2A_last_date_start) and (S2A_current_date_start < datetime.datetime.now()):
                S2A_last_date_start = S2A_current_date_start
                S2A_key = key
    if key.startswith('Sentinel-2B'):
        if not S2B_last_date_start:
            S2B_last_date_start =  datetime.datetime.strptime(key.split('_')[-2],dateformat) #from date
            if S2B_last_date_start > datetime.datetime.now():
                S2B_last_date_start = None
                S2B_key = key
            else:
                S2B_key = key
        else:
            S2B_current_date_start = datetime.datetime.strptime(key.split('_')[-2],dateformat)
            S2B_current_date_end = datetime.datetime.strptime(key.split('_')[-1].split('.')[0],dateformat)
            if (S2B_current_date_start > S2B_last_date_start) and (S2B_current_date_start < datetime.datetime.now()):
                S2B_last_date_start = S2B_current_date_start
                S2B_key = key
"""
