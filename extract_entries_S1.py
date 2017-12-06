#!usr/bin/python2.7
""" Script containing method for extracting polygons within a defined AOI from
    Sentinel-1 .kml files distributed at:
    https://sentinel.esa.int/web/sentinel/missions/sentinel-1/observation-scenario/acquisition-segments

	USAGE:
        - "python scriptname.py" in bash cmd

	COMMENTS:
		- Only works for Sentinel-1 satellites at the moment.

===========================================================
Name:          extract_entries_S1.py
Author(s):     Trygve Halsne 29.11.2017 (dd.mm.YYYY)
Modifications:
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""
import lxml.etree as ET
import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr
import codecs
import os

def extract_S1_entries(infile, outfile, outpath):
    """ Method for extracting entries in a predifined AOI. Works for the
        current setup for sentinel-1.kml files."""

    # Defining Norwegian area of interest:
    norwegian_AOI_poly = "POLYGON((-29.307389598466298 55.7151475256469,34.51470787304025 55.7151475256469,34.51470787304025 83.54659771121828,-29.307389598466298 83.54659771121828,-29.307389598466298 55.7151475256469))"
    norwegian_AOI_wtk_polygon =  ogr.CreateGeometryFromWkt(norwegian_AOI_poly)

    infile_tree = ET.parse(infile)
    infile_root = infile_tree.getroot()
    nsmap = infile_root.nsmap[None]
    find_prefix = './/{' + nsmap + '}'

    for pm in infile_tree.findall(find_prefix + 'Placemark'):
        coordinates = pm.find(find_prefix+'coordinates').text.split()

        lat = []
        lon = []
        delimiter = ','
        for i, pair in enumerate(coordinates):
            coordinates[i] = pair.replace(',', ' ')

        placemark_polygon = "POLYGON (( %s ))" % delimiter.join(coordinates)
        placemark_wtk_polygon =  ogr.CreateGeometryFromWkt(placemark_polygon)
        norwegian_AOI_intersection = norwegian_AOI_wtk_polygon.Intersects(placemark_wtk_polygon)

        if not norwegian_AOI_intersection:
            pm.getparent().remove(pm)

    try:
        output = codecs.open(str(outpath + outfile) ,'w','utf-8')
        infile_tree.write(output,encoding='utf-8',method='xml',pretty_print=True)
        output.close()
        return True
    except:
        print "Could not write %s to %s" %(infile, str(outpath + outfile))
        return True


def main():
    infile = 'Sentinel-1B_MP_20171115T160000_20171207T180000.kml'
    outpath = os.getcwd() + '/'
    outfile = 'test_s1.kml'
    extrac_values = extract_S1_entries(infile, outfile, outpath)
    if extrac_values:
        print "Script worked!"

if __name__=='__main__':
    main()
