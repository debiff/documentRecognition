__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis
from MHS.classes.region import Region
from MHS.classes.region_collector import RegionCollector
import manager.filter as component_filter
from manager.post_processing import text_segmentation, post_processing, find_paragraph, refine_paragraph
from postProcessing.classes.line import Line
from postProcessing.classes.paragraph_collector import ParagraphCollector
import copy
from postProcessing.classes.paragraph import Paragraph
import numpy as np

timer = datetime.now()
region_collector = RegionCollector()
img, gray = image.load_and_gray('./samples/00000190.jpg')
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

post_processing(region_collector.region_tree.get_node(region_collector.region_tree.root).data, binary)

region_collector.region_tree.get_node(region_collector.region_tree.root).data.included.manually_clear_cache()
region_collector.region_tree.get_node(region_collector.region_tree.root).data.manually_clear_cache()

text_tree = RegionCollector()
text_tree.add_region(region_collector.region_tree.get_node(region_collector.region_tree.root).data)

t_lines = text_segmentation(text_tree.region_tree.get_node(text_tree.region_tree.root).data)

p_collector = find_paragraph(t_lines)
p_collector = refine_paragraph(p_collector)
p_list = []

i = 0
for p in p_collector.as_list():
    img_test = copy.deepcopy(img)
    for l in p.line_collector.as_list():
        component.draw_rect(img_test, l.xmin, l.ymin, l.xmax, l.ymax, (255, 0, 0))
    cv2.imwrite('./samples/split/line/' + str(i) + '.png', img_test)
    i += 1


def contour_paragraph(lines):
    lines = sorted(lines, key=lambda l: l.ymin)
    i = 1
    pt_left = [[lines[0].xmin, lines[0].ymin]]
    pt_right = [[lines[0].xmax, lines[0].ymin]]

    while i < len(lines):
        # manage left side
        if pt_left[len(pt_left) - 1][0] < lines[i].xmin or pt_left[len(pt_left) - 1][0] > lines[i].xmin:
            pt_left.append([lines[i - 1].xmin, lines[i - 1].ymax])
            pt_left.append([lines[i].xmin, lines[i - 1].ymax])

        # manage right side
        if pt_right[len(pt_right) - 1][0] < lines[i].xmax or pt_right[len(pt_right) - 1][0] > lines[i].xmax:
            pt_right.append([lines[i - 1].xmax, lines[i - 1].ymax])
            pt_right.append([lines[i].xmax, lines[i - 1].ymax])
        i += 1
    pt_left.append([lines[len(lines) - 1].xmin, lines[len(lines) - 1].ymax])
    pt_right.append([lines[len(lines) - 1].xmax, lines[len(lines) - 1].ymax])
    cont = []
    cont.extend(pt_left)
    cont.extend(reversed(pt_right))
    return cont

for p in p_collector.as_list():
    c = np.array(contour_paragraph(p.line_collector.as_list()))
    c = c.reshape((-1,1,2))
    cv2.drawContours(img,[c],0,(147,0,255),2)
cv2.imwrite('./samples/split/contorni.png', img)



# for p in p_list:
#     l_bb_list = np.array([list(l.bounding_box) for l in p])
#     l_bb_pt = l_bb_list.reshape((-1,1,2))
#     hull = cv2.convexHull(l_bb_pt)
#     cv2.drawContours(img, [hull], 0, (147, 0, 255), 2)
# #cv2.imwrite('./samples/split/convex_hull.png', img)

    # x_min = min(l.xmin for l in p)
    # x_max = max(l.xmax for l in p)
    # y_min = min(l.ymin for l in p)
    # y_max = max(l.ymax for l in p)
    # p_collector.add(Paragraph(x_min, y_min, x_max, y_max))

#return an array of points in counterclockwise order
# def refine_paragraph(l_list):
#     ordered_lines = sorted(l_list, key=lambda l: l.ymin)
#     while len(ordered_lines == 1):
#         if ordered_lines[0].ymin <= ordered_lines[1].ymin <= ordered_lines[0].ymax:


for l in t_lines.as_list():
    component.draw_rect(img, l.xmin, l.ymin, l.xmax, l.ymax, (255,0,0))
cv2.imwrite('./samples/split/line.png', img)

for p in p_collector.as_list():
    component.draw_rect(img, p.xmin, p.ymin, p.xmax, p.ymax, (255, 0, 0))

cv2.imwrite('./samples/split/region.png', img)

region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root.png', 'text')
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root_non_text.png', 'non-text')
print((datetime.now()-timer))