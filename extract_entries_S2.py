#!usr/bin/python2.7
""" Script containing method for extracting polygons within a defined AOI from
    Sentinel-2 .kml files distributed at
    https://sentinel.esa.int/web/sentinel/missions/sentinel-2/acquisition-plans

	USAGE:
        - python "scriptname.py" in bash cmd

	COMMENTS:
		- Only works for Sentinel-2 satellites at the moment. Include Sentinel-1

===========================================================
Name:          extract_entries_S2.py
Author(s):     Trygve Halsne 22.11.2017 (dd.mm.YYYY)
Modifications:
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""
import lxml.etree as ET
import numpy as np
from osgeo import ogr
import codecs
import os

def extract_S2_entries(infile, outfile, outpath):
    """ Method for extracting entries in a predifined AOI. Works for the
        current setup for sentinel-2.kml files."""
    # Define Area of Interest
    #norwegian_AOI_poly = "POLYGON((-29.307389598466298 55.7151475256469,34.51470787304025 55.7151475256469,34.51470787304025 83.54659771121828,-29.307389598466298 83.54659771121828,-29.307389598466298 55.7151475256469))"
    #norwegian_AOI_wtk_polygon =  ogr.CreateGeometryFromWkt(norwegian_AOI_poly)
    AOI = ["POLYGON((2.68 58.06,2.68 58.06,8.57 57.83,12.26 58.94,14.02 63.65,20.26 68.16,35.46 69.31,28.34 74.67,16.39 74.86,2.68 64.50,2.68 58.06,2.68 58.06))", #mainland & bjornoya
           "POLYGON((17.82 75.14,26.67 74.99,52.09 80.33,52.37 84.80,-20.72 84.78,-3.30 77.37,17.82 75.14,17.82 75.14))", # Svalbard with surrounding
           "POLYGON((-11.25 70.43,-5.03 70.43,-5.03 71.72,-11.25 71.72,-11.25 70.43))"# Jan Mayen
           ]
    polygons = [ogr.CreateGeometryFromWkt(AOI[i]) for i in range(len(AOI))]
    #print polygons
    #for polygon in AOI:
    #    norwegian_AOI_wtk_polygon =  ogr.CreateGeometryFromWkt(norwegian_AOI_poly)


    infile_tree = ET.parse(infile)
    infile_root = infile_tree.getroot()
    nsmap = infile_root.nsmap[None]
    find_prefix = './/{' + nsmap + '}'
    folders = infile_tree.findall(find_prefix + 'Folder')

    # Only extracting NOMINAL mode
    for folder in folders:
        name = folder.find(find_prefix + 'name')
        if name.text == 'NOBS':
            placemark_folder = folder
        elif name.text == 'NOT_RECORDING':
            folder.getparent().remove(folder)
        elif name.text == 'VIC':
            folder.getparent().remove(folder)
        elif name.text == 'DARK-O':
            folder.getparent().remove(folder)


    for pm in placemark_folder.findall(find_prefix + 'Placemark'):
        coordinates = pm.find(find_prefix+'coordinates').text.split()

        lat = []
        lon = []
        delimiter = ','
        for i, pair in enumerate(coordinates):
            coordinates[i] = pair.replace(',', ' ')

        placemark_polygon = "POLYGON (( %s ))" % delimiter.join(coordinates)
        placemark_wtk_polygon =  ogr.CreateGeometryFromWkt(placemark_polygon)
        intersects = []
        for polygon in polygons:
            intersects.append(polygon.Intersects(placemark_wtk_polygon))
        #norwegian_AOI_intersection = norwegian_AOI_wtk_polygon.Intersects(placemark_wtk_polygon)
        #print intersects

        #if not norwegian_AOI_intersection:
        if not any(intersects):
            pm.getparent().remove(pm)
        #else:
        #    vis = pm.find(find_prefix + 'visibility')
        #    vis.text = '1'

    try:
        output = codecs.open(str(outpath + outfile) ,'w','utf-8')
        infile_tree.write(output,encoding='utf-8',method='xml',pretty_print=True)
        output.close()
        return True
    except:
        print "Could not write %s to %s" %(infile, str(outpath + outfile))
        return True

def main():
    infile = 'Sentinel-2A_MP_ACQ__KML_20170824T110000_20170910T140000.kml'
    infile = 'S2A_acquisition_plan.kml'
    #infile = '/home/trygveh/Sentinel-2A_MP_ACQ_KML_20180205T110000_20180219T140000.kml'
    outpath = os.getcwd() + '/'
    outfile = 'test.kml'
    extrac_values = extract_S2_entries(infile, outfile, outpath)
    if extrac_values:
        print "Script worked!"

if __name__=='__main__':
    main()
