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
    right = np.where(((comp.same_row.as_matrix_bb()[:, 0] - comp.xmax) > 0))[0].tolist()
    left = np.where(((comp.xmin - comp.same_row.as_matrix_bb()[:, 2]) > 0))[0].tolist()
    nnr = comp.same_row.as_list()[right[np.argmin(comp.same_row.as_matrix_bb()[right][:, 0])]] if len(right) > 0 else -1
    nnl = comp.same_row.as_list()[left[np.argmax(comp.same_row.as_matrix_bb()[left][:, 2])]] if len(left) > 0 else -1
    return nnr, nnl


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
        same_column = cc_same_column_new(component_collector.as_matrix_bb(), comp)
        comp.same_column = [component_collector.as_list()[c] for c in same_column]

        same_row = cc_same_row_new(component_collector.as_matrix_bb(), comp)
        comp.same_row = [component_collector.as_list()[c] for c in same_row]

        inner_components = inner_bb_new(component_collector.as_matrix_bb(), comp)
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


def inner_bb_new(cc_array, comp):
    list_inner = np.where(
        ((comp.xmin < cc_array[:, 0]) & (cc_array[:, 2] < comp.xmax) & (cc_array[:, 0] < cc_array[:, 2])) &
        ((comp.ymin < cc_array[:, 1]) & (cc_array[:, 3] < comp.ymax) & (cc_array[:, 1] < cc_array[:, 3])))
    return list_inner[0]
