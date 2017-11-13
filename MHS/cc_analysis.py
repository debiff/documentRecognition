import numpy as np
import cv2
from MHS.classes import component


__author__ = 'Simone Biffi'


def cc_area(contour):
    return cv2.contourArea(contour)


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
def cc_same_column(cc_array, cc):
    return list(np.where((np.maximum(cc_array[:, 0], cc.get_xmin()) - np.minimum(cc_array[:, 2], cc.get_xmax())) < 0))


# cc_array -> numpy.array contente tutti i cc del documento nella forma [xmin, ymin, xmax, ymax]
# cc -> singolo cc, oggetto classes/component
def cc_same_row(cc_array, cc):
    return list(np.where((np.maximum(cc_array[:, 1], cc.get_ymin()) - np.minimum(cc_array[:, 3], cc.get_ymax())) < 0))


def density(a_cc, a_bb):
    return a_cc/a_bb


def create_component(contours_list, t_area, t_density):
    rect = {}
    id_r = 0
    list_arr = []

    for cont in contours_list:
        area = cv2.contourArea(cont)
        x, y, w, h = cv2.boundingRect(cont)
        if area > t_area and density(area, w * h) > t_density:
            #ratio = w / h
            cc = component.Component(id_r, x, y, x + w, y + h, cont)
            rect[id_r] = [cc]
            list_arr.append([x, y, x + w, y + h])
            id_r += 1
    cc_arr = np.array(list_arr)

    for index, cc in rect.items():
        cc[0].set_same_column(cc_same_column(cc_arr, cc[0]))
        cc[0].set_same_row(cc_same_row(cc_arr, cc[0]))
        cc[0].set_inner_bb(inner_bb(cc_arr, cc[0]))
    return rect, cc_arr


def inner_bb(cc_array, cc):
    list_inner = np.where(
        ((cc.get_xmin() < cc_array[:, 0]) & (cc_array[:, 2] < cc.get_xmax()) & (cc_array[:, 0] < cc_array[:, 2])) &
        ((cc.get_ymin() < cc_array[:, 1]) & (cc_array[:, 3] < cc.get_ymax()) & (cc_array[:, 1] < cc_array[:, 3])))
    return len(list_inner[0])


def copy_element(img, rect_list, path=None):
    mask = np.zeros(img.shape, dtype=np.uint8)
    masked_image = np.zeros(img.shape, dtype=np.uint8)
    channel_count = img.shape[2]
    ignore_mask_color = (255,) * channel_count
    for index, cc in rect_list.items():
        if (cc[0].get_bb_width() * cc[0].get_bb_height()) > 200:
            pts = cc[0].get_contour()
            cv2.fillConvexPoly(mask, pts, ignore_mask_color)
            masked_image = np.bitwise_or(masked_image, cv2.bitwise_and(img, mask))

    if path != None:
        cv2.imwrite('./samples/textElement.png', masked_image)

    return masked_image