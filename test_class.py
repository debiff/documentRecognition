__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis
from MHS.classes.region import Region
from MHS.classes.region_collector import RegionCollector
import numpy as np
import manager.filter as component_filter
import math
from manager.post_processing import text_segmentation
import copy
from postProcessing.classes.paragraph import Paragraph
from postProcessing.classes.paragraph_collector import ParagraphCollector

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


def intersect_x(matrix, xmin, xmax):
    intersect_xmin = np.bitwise_and(matrix[:, 0] >= xmin, matrix[:, 0] <= xmax)
    intersect_xmax = np.bitwise_and(matrix[:, 2] >= xmin, matrix[:, 2] <= xmax)
    intersect = np.bitwise_or(intersect_xmin, intersect_xmax)
    intersect = np.where(intersect)
    return intersect[0].tolist()


def intersect_y(matrix, ymin, ymax):
    intersect_ymin = np.bitwise_and(matrix[:, 1] >= ymin, matrix[:, 1] <= ymax)
    intersect_ymax = np.bitwise_and(matrix[:, 3] >= ymin, matrix[:, 3] <= ymax)
    intersect = np.bitwise_or(intersect_ymin, intersect_ymax)
    intersect = np.where(intersect)
    return intersect[0].tolist()


def find_paragraph(line_coll):
    regions = []
    region = []
    for line in line_coll.as_list():
        line_height = line.ymax - line.ymin
        inter_x_id = intersect_x(line_coll.as_matrix(), line.xmin, line.xmax)
        inter_x = [line_coll.as_list()[l] for l in inter_x_id]
        inter_x = sorted(inter_x, key=lambda l: l.ymin)
        line_idx = inter_x.index(line)
        inter_x = inter_x[line_idx + 1:]    # ordered by ymin
        inter_x = list(filter(lambda x: (x.ymin - line.ymax) < min(line_height, x.ymax - x.ymin) / 1.5, inter_x))
        if len(inter_x) != 0:
            inter_x_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in inter_x])
            belows = [inter_x[0]]
            inter_y_id = intersect_y(inter_x_matrix, belows[0].ymin, belows[0].ymax)
            inter_y = [inter_x[l] for l in inter_y_id]
            below_idx = inter_y.index(belows[0])
            inter_y.pop(below_idx)
            not_comparable = []
            if len(inter_y) > 1:
                not_comparable = list(filter(lambda x: (line_height > 1.5 * (x.ymax - x.ymin)) or
                                                       ((x.ymax - x.ymin) > 1.5 * line_height), inter_y))
            if len(inter_y) > 0 and len(not_comparable) == 0:
                belows.extend(inter_y)
            line.below_lines = belows

    lines = copy.deepcopy(line_coll.as_list())
    lines = sorted(lines, key=lambda l: l.ymin)
    while len(lines) > 0:
        line = lines[0]
        region = [line]
        find_text_column(line, region)
        for l in region:
            if l in lines:
                l_idx = lines.index(l)
                lines.pop(l_idx)
        regions.append(region)
    return regions


def find_text_column(line, region_list):
    if len(line.below_lines) == 0:
        return
    for l in line.below_lines:
        if l not in region_list:
            region_list.append(l)
        find_text_column(l, region_list)


p_list = find_paragraph(t_lines)

p_collector = ParagraphCollector()
for p in p_list:
    x_min = min(l.xmin for l in p)
    x_max = max(l.xmax for l in p)
    y_min = min(l.ymin for l in p)
    y_max = max(l.ymax for l in p)
    p_collector.add(Paragraph(x_min, y_min, x_max, y_max))

for p in p_collector.as_list():
    component.draw_rect(img, p.xmin, p.ymin, p.xmax, p.ymax, (255, 0, 0))

cv2.imwrite('./samples/split/region.png', img)


for l in t_lines.as_list():
    component.draw_rect(img, l.xmin, l.ymin, l.xmax, l.ymax, (255,0,0))
cv2.imwrite('./samples/split/line.png', img)
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root.png', 'text')
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root_non_text.png', 'non-text')
print((datetime.now()-timer))