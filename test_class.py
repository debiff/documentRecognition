__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis
from MHS.classes.region import Region
from MHS.classes.region_collector import RegionCollector
import manager.filter as component_filter
from manager.post_processing import text_segmentation, post_processing, find_paragraph, refine_paragraph
from result_statistics.manager import text_statistics

timer = datetime.now()
region_collector = RegionCollector()
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)
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

# DRAW LINE, PARAGRAPH, TEXT COMPONENT, NON TEXT COMPONENT
# img_line = copy.deepcopy(img)
# for p in p_collector.as_list():
#     for l in p.line_collector.as_list():
#         component.draw_rect(img_line, l.xmin, l.ymin, l.xmax, l.ymax, (255, 0, 0))
# cv2.imwrite('./samples/result/line.png', img_line)
#
# img_paragraph = copy.deepcopy(img)
# for p in p_collector.as_list():
#     cv2.drawContours(img_paragraph,[p.contour], 0, (147, 0, 255), 2)
# cv2.imwrite('./samples/result/paragraph.png', img_paragraph)
#
# region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/result/text.png', 'text')
# region_collector.region_tree.get_node(region_collector.region_tree.root).data.save('./samples/result/non_text.png', 'non-text')

text_statistics(img, p_collector)

print((datetime.now()-timer))