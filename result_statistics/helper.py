import cv2
import numpy as np
import xml.etree.ElementTree as ET


def accuracy(img, paragraph, ground_truth, out_path):
    height, width, _ = img.shape
    p_image = np.zeros((height, width))
    gt_image = np.zeros((height, width))
    for p in paragraph.as_list():
        cv2.drawContours(p_image,[p.contour], 0, (147, 0, 255), -1)
    cv2.imwrite(out_path + '_p_filled.png', p_image)

    for c in ground_truth:
        cv2.drawContours(gt_image,[c], 0, (147, 0, 255), -1)
    cv2.imwrite(out_path + '_gt_filled.png', gt_image)

    intersection = np.multiply(p_image, gt_image)
    cv2.imwrite(out_path + '_intersection.png', intersection)

    not_found = intersection.copy()
    not_found[not_found == 0] = -1
    not_found[not_found > 0] = 0
    not_found[not_found == -1] = 147

    not_found = np.multiply(not_found, gt_image)

    cv2.imwrite(out_path + '_not_found.png', not_found)
    recall = np.count_nonzero(intersection) / np.count_nonzero(gt_image)
    precision = np.count_nonzero(intersection) / np.count_nonzero(p_image)
    return recall, precision


def extract_gt_contours(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    text_coord = []
    non_text_coord = []
    for region in root[1]:
        c = []
        for coord in region[0]:
            x = int(coord.attrib['x'])
            y = int(coord.attrib['y'])
            c.append([x, y])
        c = np.array(c)
        c = c.reshape((-1, 1, 2))
        if region.tag.find('TextRegion') > -1:
            text_coord.append(c)
        else:
            non_text_coord.append(c)
    return text_coord, non_text_coord

