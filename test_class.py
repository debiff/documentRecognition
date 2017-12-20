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


def same_line(line1, line2):
    first_in_second = line2.ymin <= line1.ymin <= line2.ymax or line2.ymin <= line1.ymax <= line2.ymax
    second_in_first = line1.ymin <= line2.ymin <= line1.ymax or line1.ymin <= line2.ymax <= line1.ymax
    return first_in_second or second_in_first


def unify_line(line1, line2):
    xmin = min(line1.xmin, line2.xmin)
    ymin = min(line1.ymin, line2.ymin)
    xmax = max(line1.xmax, line2.xmax)
    ymax = max(line1.ymax, line2.ymax)
    return Line(xmin, ymin, xmax, ymax)

i = 0
while i <= len(p_list) - 1:
    p_line = sorted(p_list[i], key=lambda l: l.ymin)
    j = 0
    while j <= len(p_line) - 2:
        if same_line(p_line[j], p_line[j+1]):
            new_line = unify_line(p_line[j], p_line[j+1])
            p_line.pop(j + 1)
            p_line.pop(j)
            p_line.insert(j, new_line)
        else:
            j += 1
    p_list[i] = p_line
    i += 1
i = 0
for p in p_list:
    img_test = copy.deepcopy(img)
    for l in p:
        component.draw_rect(img_test, l.xmin, l.ymin, l.xmax, l.ymax, (255, 0, 0))
    cv2.imwrite('./samples/split/line/' + str(i) + '.png', img_test)
    i += 1
cv2.imwrite('./samples/split/line2.png', img)



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


# for l in t_lines.as_list():
#     component.draw_rect(img, l.xmin, l.ymin, l.xmax, l.ymax, (255,0,0))
# cv2.imwrite('./samples/split/line.png', img)
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root.png', 'text')
region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/split/root_non_text.png', 'non-text')
print((datetime.now()-timer))