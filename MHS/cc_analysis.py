import numpy as np
import cv2
from MHS.classes.component import Component
from MHS.classes.component_collector import ComponentCollector


__author__ = 'Simone Biffi'


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
def cc_same_column_new(cc_array, comp):
    return np.where((np.maximum(cc_array[:, 0], comp.xmin) - np.minimum(cc_array[:, 2], comp.xmax)) < 0)[0]\
        .tolist()


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
def cc_same_row_new(cc_array, comp):
    return np.where((np.maximum(cc_array[:, 1], comp.ymin) - np.minimum(cc_array[:, 3], comp.ymax)) < 0)[0] \
        .tolist()


def neighbors_new(comp):
    right = np.where(((comp.same_row.as_matrix()[:, 0] - comp.xmax) > 0))[0].tolist()
    left = np.where(((comp.xmin - comp.same_row.as_matrix()[:, 2]) > 0))[0].tolist()
    nnr = comp.same_row.as_list()[right[np.argmin(comp.same_row.as_matrix()[right][:, 0])]] if len(right) > 0 else -1
    nnl = comp.same_row.as_list()[left[np.argmax(comp.same_row.as_matrix()[left][:, 2])]] if len(left) > 0 else -1
    return nnr, nnl


def cc_same_row(cc_array, cc):
    min_right_idx = -1
    min_left_idx = -1
    nnl = -1
    nnr = -1

    near = np.where((np.maximum(cc_array[:, 1], cc.ymin) - np.minimum(cc_array[:, 3], cc.ymax)) < 0)[0]\
        .tolist()
    right = np.where(((cc_array[:, 0] - cc.xmax) > 0))[0].tolist()
    left = np.where(((cc.xmin - cc_array[:, 2]) > 0))[0].tolist()
    near_right = list(set(near) & set(right))
    near_left = list(set(near) & set(left))
    if len(near_right) > 0:
        min_right_idx = np.argmin(cc_array[near_right][:, 0])
        nnr = near_right[min_right_idx]
    if len(near_left) > 0:
        min_left_idx = np.argmin(cc_array[near_left][:, 0])
        nnl = near_left[min_left_idx]

    return near, nnr, nnl


def density_new(a_cc, a_bb):
    return a_cc/a_bb


def hw_ratio_new(w, h):
    return min(w, h) / max(w, h)


def create_component_new(contours_list, t_area, t_density, t_ratio):
    component_collector = ComponentCollector()

    for i, cont in enumerate(contours_list):

        area = cv2.contourArea(cont)
        x, y, w, h = cv2.boundingRect(cont)

        if area > t_area and density_new(area, w * h) > t_density and hw_ratio_new(w, h) > t_ratio:
            component_collector.add_component(
                Component(i, x, y, x + w, y + h, 'text', area, cont))

    for comp in component_collector.as_list():
        same_column = cc_same_column_new(component_collector.as_matrix(), comp)
        comp.same_column = [component_collector.as_list()[c] for c in same_column]

        same_row = cc_same_row_new(component_collector.as_matrix(), comp)
        comp.same_row = [component_collector.as_list()[c] for c in same_row]

        inner_components = inner_bb_new(component_collector.as_matrix(), comp)
        comp.inner_components = [component_collector.as_list()[c] for c in inner_components]

        nnr, nnl = neighbors_new(comp)

        if nnr != -1:
            comp.nnr = nnr
            comp.nr = nnr
            nnr.nl = comp

        if nnl != -1:
            comp.nnl = nnl
            comp.nl = nnl
            nnl.nr = comp

    return component_collector


def create_component(contours_list, t_area, t_density):
    rect = {}
    id_r = 0
    list_arr = []
    for cont in contours_list:
        area = cv2.contourArea(cont)
        x, y, w, h = cv2.boundingRect(cont)
        cc = component.Component(id_r, x, y, x + w, y + h, area, cont)
        if area > t_area and density(area, w * h) > t_density and cc.hw_ratio > 0.06:
            #ratio = w / h
            rect[id_r] = [cc]
            list_arr.append([x, y, x + w, y + h])
            id_r += 1
    cc_arr = np.array(list_arr)

    for index, cc in rect.items():
        cc[0].same_column = cc_same_column(cc_arr, cc[0])
        near, nnr, nnl = cc_same_row(cc_arr, cc[0])
        cc[0].same_row = near
        if nnr > -1:
            cc[0].nr = nnr
            cc[0].nnr = nnr
            rect[nnr][0].nl = index
        if nnl > -1:
            cc[0].nl = nnl
            cc[0].nnl = nnl
            rect[nnl][0].nr = index
        cc[0].inner_components = len(inner_bb(cc_arr, cc[0]))
    return rect, cc_arr


def inner_bb_new(cc_array, comp):
    list_inner = np.where(
        ((comp.xmin < cc_array[:, 0]) & (cc_array[:, 2] < comp.xmax) & (cc_array[:, 0] < cc_array[:, 2])) &
        ((comp.ymin < cc_array[:, 1]) & (cc_array[:, 3] < comp.ymax) & (cc_array[:, 1] < cc_array[:, 3])))
    return list_inner[0]


def copy_element(img, rect_list, path=None):
    mask = np.zeros(img.shape, dtype=np.uint8)
    masked_image = np.zeros(img.shape, dtype=np.uint8)
    channel_count = img.shape[2]
    ignore_mask_color = (255,) * channel_count
    for index, cc in rect_list.items():
        if (cc[0].bb_width * cc[0].bb_height) > 200:
            pts = cc[0].get_contour()
            cv2.fillConvexPoly(mask, pts, ignore_mask_color)
            masked_image = np.bitwise_or(masked_image, cv2.bitwise_and(img, mask))

    if path != None:
        cv2.imwrite('./samples/textElement.png', masked_image)

    return masked_image