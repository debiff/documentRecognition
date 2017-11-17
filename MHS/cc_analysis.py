import numpy as np
import cv2
from MHS.classes import component


__author__ = 'Simone Biffi'


def cc_area(contour):
    return cv2.contourArea(contour)


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
def cc_same_column(cc_array, cc):
    return np.where((np.maximum(cc_array[:, 0], cc.xmin) - np.minimum(cc_array[:, 2], cc.xmax)) < 0)[0]\
        .tolist()


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
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


def density(a_cc, a_bb):
    return a_cc/a_bb


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
        cc[0].inner_bb = len(inner_bb(cc_arr, cc[0]))
    return rect, cc_arr


def inner_bb(cc_array, cc):
    list_inner = np.where(
        ((cc.xmin < cc_array[:, 0]) & (cc_array[:, 2] < cc.xmax) & (cc_array[:, 0] < cc_array[:, 2])) &
        ((cc.ymin < cc_array[:, 1]) & (cc_array[:, 3] < cc.ymax) & (cc_array[:, 1] < cc_array[:, 3])))
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