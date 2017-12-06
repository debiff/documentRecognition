__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter
from MHS.classes.region import Region
from MHS.classes.region_collector import RegionCollector
import numpy as np
import manager.filter as component_filter
import math
from manager.post_processing import text_segmentation

timer = datetime.now()
region_collector = RegionCollector()
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)


# num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, 4, cv2.CV_32S)
# labels[labels == 385] = 10000
# labels[labels < 10000] = 255
# labels[labels == 10000] = 0
#
# cv2.imwrite('./samples/split/labeled.png', labels)
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
comp_collector = cc_analysis.create_component_new(contours, 6, 0.15, 0.06)
print((datetime.now()-timer))

component_filter.heuristic(comp_collector, 4)
document = Region(0, 0, img.shape[1], img.shape[0], comp_collector, erode=True)

region_collector.add_region(document)

component_filter.recursive_filter(region_collector)

region_collector.region_tree.get_node(region_collector.region_tree.root).data.included.manually_clear_cache()
region_collector.region_tree.get_node(region_collector.region_tree.root).data.manually_clear_cache()


def remove_text(document, bin):
    for component in document.included.text_component().as_list():
        bin[component.ymin:component.ymax, component.xmin:component.xmax] = 255
    return bin


def fill_non_text(non_text_image, non_text_image_bb):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (math.ceil(non_text_image.shape[0] * 0.005),
                                                        math.ceil(non_text_image.shape[1] * 0.005)))
    res = cv2.morphologyEx(np.bitwise_not(non_text_image_bb), cv2.MORPH_DILATE, kernel)
    res = np.bitwise_not(res)
    res[non_text_image == 1] = 0
    return res


def compare_text_non_text(document, filled):
    for component in document.included.text_component().as_list():
        sub_image = filled[component.ymin:component.ymax, component.xmin:component.xmax]
        where = np.where(sub_image == 0)
        if len(where[0]) + len(where[1]) > 0:
            component.type = 'non_text'


def post_processing(document, bin):
    non_text = remove_text(document, bin)
    filled_non_text = fill_non_text(document.bin_pixel('non-text'), non_text)
    compare_text_non_text(document, filled_non_text)

post_processing(region_collector.region_tree.get_node(region_collector.region_tree.root).data, binary)

region_collector.region_tree.get_node(region_collector.region_tree.root).data.included.manually_clear_cache()
region_collector.region_tree.get_node(region_collector.region_tree.root).data.manually_clear_cache()

text_tree = RegionCollector()
text_tree.add_region(region_collector.region_tree.get_node(region_collector.region_tree.root).data)

t_lines = text_segmentation(text_tree.region_tree.get_node(text_tree.region_tree.root).data)





for l in t_lines.as_list():
    component.draw_rect(img, l.xmin, l.ymin, l.xmax, l.ymax, (255,0,0))
cv2.imwrite('./samples/split/line.png', img)
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root.png', 'text')
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root_non_text.png', 'non-text')
print((datetime.now()-timer))