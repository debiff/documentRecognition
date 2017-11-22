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
# loads the image and convert to grayscale
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)

#kernel = np.ones((5, 5), np.uint8)
#dilation = cv2.erode(binary, kernel, iterations=1)
# finds component through findcontours
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
comp_collector = cc_analysis.create_component_new(contours, 6, 0.15, 0.06)
print((datetime.now()-timer))

component_filter.heuristic(comp_collector, 4)
document = Region(0, 0, img.shape[1], img.shape[0], comp_collector)

region_collector.add_region(document)

recursive_filter.multilevel_classification(region_collector.region_tree.get_node(region_collector.region_tree.root), region_collector)
print((datetime.now()-timer))

def ricorsive_filter(region_collector, region):
    changed = True
    while changed:
        changed = False
        if component_filter.maximum_median(region):
            changed = True
            region.included.max_area_component.type = 'non_text'
            region.included.manually_clear_cache()
        elif component_filter.minimum_median(region):
            changed = True
            region.included.min_area_component.type = 'non_text'
            region.included.manually_clear_cache()

ricorsive_filter(region_collector, document)