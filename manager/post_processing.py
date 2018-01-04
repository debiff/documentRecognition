from postProcessing.classes.line import Line
from postProcessing.classes.line_collector import LineCollector
from postProcessing.classes.paragraph import Paragraph
from postProcessing.classes.paragraph_collector import ParagraphCollector
import statistics
import numpy as np
import math
import copy
import cv2


# Graphical and separation phase
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


def refine_non_text(filled):
    im2, contours, hierarchy = cv2.findContours(filled, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    height, width = filled.shape
    imm = np.ones((height, width), np.uint8) * 255
    cv2.drawContours(imm, contours, -1, (0,0), -1)
    imm[imm == 0] = 1
    imm[imm == 255] = 0
    imm[imm == 1] = 255
    return contours, imm


def post_processing(document, bin):
    non_text = remove_text(document, bin)
    filled_non_text = fill_non_text(document.bin_pixel('non-text'), non_text)
    _, filled_non_text = refine_non_text(filled_non_text)
    compare_text_non_text(document, filled_non_text)
    return filled_non_text


# Find line phase
def is_near(comp_left, comp_right):
    distance_height = abs(comp_right.xmin - comp_left.xmax) <= 1.2 * max(comp_left.bb_height, comp_right.bb_height)
    if distance_height:
        return True
    return False


def create_line(comp_list):
    x_min = min(c.xmin for c in comp_list)
    x_max = max(c.xmax for c in comp_list)
    y_min = min(c.ymin for c in comp_list)
    y_max = max(c.ymax for c in comp_list)

    return Line(x_min, y_min, x_max, y_max)


def find_lines(text_component):
    lines = []
    for c in text_component.as_list():
        if not (any(c in l for l in lines)):
            line = []
            same_row = c.same_row.as_list()
            line.extend(comp for comp in same_row if comp.type == 'text')
            if len(line) != 0:
                if c not in line:
                    line.append(c)
                sorted_l = sorted(line, key=lambda comp: comp.xmin)
                lines.append(sorted_l)
    return lines


def text_segmentation(text_tree):
    l_collector = LineCollector()
    component_collector = text_tree.included.text_component()
    component_lines = find_lines(component_collector)
    chains = []
    for line in component_lines:
        chain_same_line = []
        chain = [line[0]]
        for c_id in range(len(line) - 1):
            if is_near(line[c_id], line[c_id + 1]):
                chain.append(line[c_id + 1])
            else:
                chain_same_line.append(create_line(chain))
                l_collector.add_line(create_line(chain))
                chain = [line[c_id + 1]]
            if c_id + 1 == len(line) - 1:
                chain_same_line.append(create_line(chain))
                l_collector.add_line(create_line(chain))
        chains.append(chain_same_line)

    return l_collector


# Find paragraph phase
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
    paragraphs = ParagraphCollector()
    for line in line_coll.as_list():
        inter_x_id = intersect_x(line_coll.as_matrix(), line.xmin, line.xmax)
        inter_x = [line_coll.as_list()[l] for l in inter_x_id]
        inter_x = sorted(inter_x, key=lambda l: l.ymin)
        line_idx = inter_x.index(line)
        inter_x = inter_x[line_idx + 1:]    # ordered by ymin
        inter_x = list(filter(lambda x: (x.ymin - line.ymax) < min(line.height, x.height) / 1.5, inter_x))
        if len(inter_x) != 0:
            inter_x_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in inter_x])
            belows = [inter_x[0]]
            inter_y_id = intersect_y(inter_x_matrix, belows[0].ymin, belows[0].ymax)
            inter_y = [inter_x[l] for l in inter_y_id]
            below_idx = inter_y.index(belows[0])
            inter_y.pop(below_idx)
            not_comparable = []
            if len(inter_y) > 1:
                not_comparable = list(filter(lambda x: (line.height > 1.5 * x.height) or
                                                       (x.height > 1.5 * line.height), inter_y))
            if len(inter_y) > 0 and len(not_comparable) == 0:
                belows.extend(inter_y)
            line.below_lines = belows

    lines = copy.deepcopy(line_coll.as_list())
    lines = sorted(lines, key=lambda l: l.ymin)

    while len(lines) > 0:
        # line = lines[0]
        # region = [line]
        paragraph = Paragraph()
        added_line = []
        paragraph.line_collector.add_line(lines[0])
        added_line.append(lines[0])
        find_text_column(lines[0], paragraph, added_line)
        for l in added_line:
            if l in lines:
                l_idx = lines.index(l)
                lines.pop(l_idx)
        paragraphs.add_paragraph(paragraph)
    unify_duplicate(paragraphs)
    unify_included(paragraphs)
    return paragraphs


def find_text_column(line, paragraph, added_list):
    if len(line.below_lines) == 0:
        return
    for l in line.below_lines:
        if l not in paragraph.line_collector.as_list():
            paragraph.line_collector.add_line(l)
            added_list.append(l)
        find_text_column(l, paragraph, added_list)


def unify_duplicate(paragraphs):
    i = 0
    paragraphs_list = paragraphs.as_list()
    while i < len(paragraphs_list):
        new_p = None
        for p in paragraphs_list:
            if paragraphs_list[i] != p:
                if check_paragraph_duplicate(paragraphs_list[i], p):
                    new_p = unify_paragraph(paragraphs_list[i], p)
                    id_p2 = paragraphs_list.index(p)
                    if i < id_p2:
                        paragraphs_list.pop(id_p2)
                        paragraphs_list.pop(i)
                        paragraphs_list.insert(i, new_p)
                    else:
                        paragraphs_list.pop(i)
                        paragraphs_list.pop(id_p2)
                        paragraphs_list.insert(i, new_p)
                    break
        if new_p is None:
            i += 1


def check_paragraph_duplicate(p1, p2):
    return bool(set(p1.line_collector.as_list()).intersection(p2.line_collector.as_list()))


def unify_included(paragraphs):
    i = 0
    paragraphs_list = paragraphs.as_list()
    while i < len(paragraphs_list):
        new_p = None
        for p in paragraphs_list:
            if paragraphs_list[i] != p:
                if check_paragraph_included(paragraphs_list[i], p):
                    new_p = unify_paragraph(paragraphs_list[i], p)
                    id_p2 = paragraphs_list.index(p)
                    if i < id_p2:
                        paragraphs_list.pop(id_p2)
                        paragraphs_list.pop(i)
                        paragraphs_list.insert(i, new_p)
                    else:
                        paragraphs_list.pop(i)
                        paragraphs_list.pop(id_p2)
                        paragraphs_list.insert(i, new_p)
                    break
        if new_p is None:
            i += 1


def check_paragraph_included(p1, p2):
    bb1 = p1.bounding_box
    bb2 = p2.bounding_box
    dx = min(bb1[2], bb2[2]) - max(bb1[0], bb2[0])
    dy = min(bb1[3], bb2[3]) - max(bb1[1], bb2[1])
    if (dx >= 0) and (dy >= 0):
        return True


def unify_paragraph(p1, p2):
    new_p = Paragraph()
    lines = list(set(p1.line_collector.as_list()).union(p2.line_collector.as_list()))
    new_p.line_collector.add_lines(lines)
    return new_p


# Refine paragraph phase
def refine_paragraph(paragraph_collector):
    for p in paragraph_collector.as_list():
        line_list = p.line_collector.as_list()
        line_list = sorted(line_list, key=lambda l: l.ymin)
        line_collector = LineCollector()
        i = 0
        while i < len(line_list) - 1:
            if check_same_line(line_list[i], line_list[i + 1]):
                new_line = unify_line(line_list[i], line_list[i + 1])
                line_list.pop(i + 1)
                line_list.pop(i)
                line_list.insert(i, new_line)
            else:
                i += 1
        line_collector.add_lines(line_list)
        p.line_collector = line_collector

    for p in paragraph_collector.as_list():
        c = np.array(contour_paragraph(p.line_collector.as_list()))
        p.contour = c

    return paragraph_collector


def check_same_line(line1, line2):
    first_in_second = line2.ymin <= line1.ymin <= line2.ymax or line2.ymin <= line1.ymax <= line2.ymax
    second_in_first = line1.ymin <= line2.ymin <= line1.ymax or line1.ymin <= line2.ymax <= line1.ymax
    return first_in_second or second_in_first


def unify_line(line1, line2):
    xmin = min(line1.xmin, line2.xmin)
    ymin = min(line1.ymin, line2.ymin)
    xmax = max(line1.xmax, line2.xmax)
    ymax = max(line1.ymax, line2.ymax)
    return Line(xmin, ymin, xmax, ymax)


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
    cont = np.array(cont)
    cont = cont.reshape((-1, 1, 2))
    return cont


# Clear non text element
def find_non_text_element(p_collector, non_text_img):
    height, width = non_text_img.shape
    text_img = np.ones((height, width), np.uint8) * 255
    for p in p_collector.as_list():
        cv2.drawContours(text_img, [p.contour], 0, 0, -1)
    text_img[text_img == 0] = 0
    text_img[text_img == 255] = 1

    non_text_img[non_text_img == 0] = 1
    non_text_img[non_text_img == 255] = 0
    result = np.multiply(text_img, non_text_img)
    result[result == 0] = 255
    result[result == 1] = 0

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (math.ceil(height * 0.009),
                                                        math.ceil(width * 0.009)))
    result = cv2.morphologyEx(np.bitwise_not(result), cv2.MORPH_CLOSE, kernel)
    result = np.bitwise_not(result)

    im2, contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(result, contours, -1, 0, 3)
    return result
