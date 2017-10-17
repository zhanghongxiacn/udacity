#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Sat Oct  7 16:17:11 2017

@author: Zhanghongxia
"""
import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "chengdu_china.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
    output.write('<osm>\n  '.encode('utf-8'))

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>'.encode('utf-8'))
