__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter
from MHS.classes.region import Region
from MHS.classes.region_collector import RegionCollector
import numpy as np
import manager.filter as component_filter

timer = datetime.now()
region_collector = RegionCollector()
img, gray = image.load_and_gray('./samples/0001.jpg')
binary = image.binarize(gray)

contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
comp_collector = cc_analysis.create_component_new(contours, 6, 0.15, 0.06)
print((datetime.now()-timer))

component_filter.heuristic(comp_collector, 4)
document = Region(0, 0, img.shape[1], img.shape[0], comp_collector, erode=True)

region_collector.add_region(document)


a = [x for x in region_collector.region_tree.get_node(region_collector.region_tree.root).data.included.text_component().as_list() if x.type == 'non_text']
component_filter.recursive_filter(region_collector)


region_collector.region_tree.get_node(region_collector.region_tree.root).data.included.manually_clear_cache()
region_collector.region_tree.get_node(region_collector.region_tree.root).data.manually_clear_cache()
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root.png', 'text')
