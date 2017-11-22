import cv2
import numpy as np
import math
from statistics import median
from MHS import hre
from MHS.classes.component import Component
from MHS.classes.component_collector import ComponentCollector
from MHS.classes.region import Region
from MHS import cc_analysis
from datetime import datetime


def homogeneity(node, direction):
    region = node.data
    if direction == 'vertical' and (region.vertical_variance_black > 1.3 or region.vertical_variance_white > 1.3):
        max_black = np.amax(region.vertical_black)
        max_white = np.amax(region.vertical_white)
        if ((region.vertical_variance_black > region.vertical_variance_white) and (max_black > region.vertical_median_black)) or\
            ((region.vertical_variance_white > region.vertical_variance_black) and (max_white > region.vertical_median_white)):
            return False

    if direction == 'horizontal' and region.horizontal_variance_black > 1.3 and region.horizontal_variance_white > 1.3:
        max_black = np.amax(region.horizontal_black)
        max_white = np.amax(region.horizontal_white)
        if ((region.horizontal_variance_black > region.horizontal_variance_white) and (max_black > region.horizontal_median_black)) or\
            ((region.horizontal_variance_white > region.horizontal_variance_black) and (max_white > region.horizontal_median_white)):
            return False

    return True


def split(node, direction, region_collector):
    node_id = node.identifier
    region = node.data
    splitted_region = []

    if direction == 'vertical':
        if region.vertical_variance_black > region.vertical_variance_white:
            splitted_region = split_black(region, direction)
        else:
            splitted_region = split_white(region, direction)

    elif direction == 'horizontal':
        if region.horizontal_variance_black > region.horizontal_variance_white:
            splitted_region = split_black(region, direction)
        else:
            splitted_region = split_white(region, direction)

    region_collector.add_regions(splitted_region, node_id)


def split_black(region, direction):
    rle = region.vertical_rle if direction == 'vertical' else region.horizontal_rle
    i_max_black = np.argmax(region.vertical_black) if direction == 'vertical' else np.argmax(region.horizontal_black)
    i_max_rle = ((i_max_black + 1) * 4) - 1 if rle[0] == 0 else (i_max_black * 4) + 1
    bb_list = []
    region_list = []
    count = 0
    for i in range(1, i_max_rle + 1, 2):
        if (i_max_rle == i == 1) or (i_max_rle == i + 2 == 3):
            """
            Cut first black space and region start with black space
            |------    ---   ---   ---|

            or

            Cut first black space and region start with white space
            |    -----   ---   ---|

            """
            count += rle[i] + rle[i + 2]

            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_right])
            break

        elif (i_max_rle == i + 2 == len(rle) - 1) or (i_max_rle + 2 == i + 2 == len(rle) - 1):
            """
            Cut last black space and region end with black space
            |    ---   ---   -----|

            or

            Cut last black space and region end with white space
            |---   ---   -----   |
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_right])
            break

        elif i + 2 == i_max_rle:
            """
            Cut black space among two white space
            |---   ---   ----------   ---|
            """
            count += math.ceil(rle[i] / 2)
            cut_left = count

            region_left = [region.xmin, region.ymin, region.xmin + cut_left, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + cut_left]

            count += math.floor(rle[i] / 2) + rle[i + 2] + math.ceil(rle[i + 4] / 2)
            cut_right = count

            region_center = [region.xmin + cut_left + 1, region.ymin, region.xmin + cut_right, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + cut_left + 1, region.xmax, region.ymin + cut_right]

            region_right = [region.xmin + cut_right + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + cut_right + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_center, region_right])
            break

        else:
            count += rle[i]

    for bb in bb_list:
        bb_comp = Component(None, bb[0], bb[1], bb[2], bb[3])
        comp_collector = ComponentCollector()
        inner_components = cc_analysis.inner_bb_new(region.included.as_matrix_bb(), bb_comp)
        comp_collector.add_components([region.included.as_list()[c] for c in inner_components])
        region_list.append(Region(bb[0], bb[1], bb[2], bb[3], comp_collector))

    return region_list


def split_white(region, direction):
    rle = region.vertical_rle if direction == 'vertical' else region.horizontal_rle
    i_max_white = np.argmax(region.vertical_white) if direction == 'vertical' else np.argmax(region.horizontal_white)
    i_max_rle = ((i_max_white + 1) * 4) - 1 if rle[0] == -1 else (i_max_white * 4) + 1
    bb_list = []
    region_list = []
    count = 0
    for i in range(1, i_max_rle + 1, 2):
        if (i_max_rle == i == 1) or (i_max_rle == i == 3):
            """
            Cut first white space and region start with white space
            |       ---    ---   ---   ---|

            or

            Cut first white space and region start with black space
            |---       ---   ---   ---|
            """
            count += rle[i]
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
            break

        elif (i_max_rle == i == len(rle) - 1) or ((i_max_rle + 2) == (i + 2) == len(rle) - 1):
            """
            Cut last white space and region end with white space
            |---    ---   ---   ---        |

            or

            Cut first white space and region end with black space
            |---    ---   ---           ---|
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
            break

        elif i_max_rle == i:
            """
            Cut last white space between two black space
            |---    ---            ---   ---|
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            count += rle[i]
            region_right = [region.xmin + count, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
        else:
            count += rle[i]

    for bb in bb_list:
        bb_comp = Component(None, bb[0], bb[1], bb[2], bb[3])
        comp_collector = ComponentCollector()
        inner_components = cc_analysis.inner_bb_new(region.included.as_matrix_bb(), bb_comp)
        comp_collector.add_components([region.included.as_list()[c] for c in inner_components])
        region_list.append(Region(bb[0], bb[1], bb[2], bb[3], comp_collector))

    return region_list


def recursive_splitting(node, direction, region_collector):
    if homogeneity(node, direction):
        return
    split(node, direction, region_collector)
    for leaves in region_collector.region_tree.leaves(node.identifier):
        recursive_splitting(leaves, direction, region_collector)


def multilevel_classification(node, region_collector):
    recursive_splitting(node, 'vertical', region_collector)
    for leaves in region_collector.region_tree.leaves(node.identifier):
        recursive_splitting(leaves, 'horizontal', region_collector)



def vertical_homogeneity(region, xmin, ymin):
    region = np.copy(region)
    #region[region == 0] = 1
    #region[region == 255] = 0
    # for every x sum the y
    vertical_h = np.sum(region, axis=0)
    switched = hre.switch(0, -1, vertical_h)
    rle = hre.run_lenght_encoding(switched)
    b, w = hre.separate_b_w(rle)
    medb = math.ceil(median(b)) if (b.size > 0) else 0
    medw = math.ceil(median(w)) if (w.size > 0) else 0
    varb = hre.variance(b) if (b.size > 0) else 0
    varw = hre.variance(w) if (w.size > 0) else 0
    splitted_bb = []
    idx_split = []
    xmax = xmin + region.shape[1]
    ymax = ymin + region.shape[0]
    homogeneous = False
    if varb > 1.3 and varb > varw:
        maxb = np.amax(b)
        if maxb > medb:
            imaxb = np.argmax(b)
            countb = -1

            idx_split_count = 0
            i = 0
            while countb != imaxb:
                if rle[i] == -1:
                    countb += 1

                if imaxb == 0 and countb == 0 and i == 0:
                    idx_split_count += rle[i + 1] + math.floor(rle[i + 3] / 2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmin + idx_split_count, ymax))
                    splitted_bb.append((xmin + idx_split_count, ymin, xmax, ymax))
                elif countb + 1 >= imaxb and rle[i] == 0:
                    idx_split_count += math.floor((rle[i + 1]) / 2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmin + idx_split_count, ymax))

                    if (i + 5) < rle.size:
                        splitted_bb.append((xmin + idx_split_count + 1, ymin, xmin + idx_split_count + math.ceil((rle[i + 1]) / 2) + rle[i + 3]
                                            + math.floor((rle[i + 5]) / 2), ymax))
                        idx_split_count += math.ceil((rle[i + 1]) / 2) + rle[i + 3] + math.floor((rle[i + 5]) / 2)
                        idx_split.append(idx_split_count)

                    splitted_bb.append((xmin + idx_split_count, ymin, xmax, ymax))
                    countb += 1
                else:
                    idx_split_count += rle[i + 1]
                i += 2
        else:
            homogeneous = True
    elif varw > 1.3 and varw > varb:
        maxw = np.amax(w)
        if maxw > medw:
            imaxw = np.argmax(w)
            countw = -1
            idx_split_count = 0
            i = 0
            while countw != imaxw:
                if rle[i] == 0:
                    countw += 1
                if countw >= imaxw:
                    idx_split_count += math.floor((rle[i + 1]) / 2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmin + idx_split_count, ymax))
                    splitted_bb.append((xmin + idx_split_count + 1, ymin, xmax, ymax))
                else:
                    idx_split_count += rle[i + 1]
                i += 2
        else:
            homogeneous = True
    else: homogeneous = True

    if homogeneous:
        splitted_bb.append((xmin, ymin, xmax, ymax))
    splitted_region = np.array_split(region, idx_split, axis=1)

    return homogeneous, splitted_region, splitted_bb


def horizontal_homogeneity(region, xmin, ymin):
    region = np.copy(region)
    region[region == 0] = 1
    region[region == 255] = 0
    # for every y sum the x
    horizontal_h = np.sum(region, axis=1)
    switched = hre.switch(0, -1, horizontal_h)
    rle = hre.run_lenght_encoding(switched)
    b, w = hre.separate_b_w(rle)
    medb = math.ceil(median(b)) if (b.size > 0) else 0
    medw = math.ceil(median(w)) if (w.size > 0) else 0
    varb = hre.variance(b) if (b.size > 0) else 0
    varw = hre.variance(w) if (w.size > 0) else 0
    splitted_bb = []
    idx_split = []
    xmax = xmin + region.shape[1]
    ymax = ymin + region.shape[0]
    homogeneous = False
    if varb > 1.3 and varb > varw:
        maxb = np.amax(b)
        if maxb > medb:
            imaxb = np.argmax(b)
            countb = -1

            idx_split_count = 0
            i = 0
            while countb != imaxb:
                if rle[i] == -1:
                    countb += 1
                if imaxb == 0 and countb == 0 and i == 0:
                    idx_split_count += rle[i + 1] + math.floor(rle[i + 3] / 2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmax, ymin + idx_split_count))
                    splitted_bb.append((xmin, ymin + idx_split_count + 1, xmax, ymax))
                elif countb + 1 >= imaxb and rle[i] == 0:
                    idx_split_count += math.floor((rle[i+1])/2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmax, ymin + idx_split_count))
                    if(i+5) < rle.size:
                        splitted_bb.append((xmin, ymin + idx_split_count + 1, xmax, ymin + idx_split_count + math.ceil((rle[i+1])/2) + rle[i + 3]
                                            + math.floor(rle[i + 5] / 2)))
                        idx_split_count += math.ceil((rle[i+1])/2) + rle[i + 3] + math.floor(rle[i + 5] / 2)
                        idx_split.append(idx_split_count)

                    splitted_bb.append((xmin, ymin + idx_split_count + 1, xmax, ymax))
                else:
                    idx_split_count += rle[i + 1]
                i += 2
        else:
            homogeneous = True
    elif varw > 1.3 and varw > varb:
        maxw = np.amax(w)
        if maxw > medw:
            imaxw = np.argmax(w)
            countw = -1
            idx_split_count = 0
            i = 0
            while countw != imaxw:
                if rle[i] == 0:
                    countw += 1
                if countw >= imaxw:
                    idx_split_count += math.floor((rle[i + 1]) / 2)
                    idx_split.append(idx_split_count)
                    splitted_bb.append((xmin, ymin, xmax, ymax + idx_split_count))
                    splitted_bb.append((xmin, ymin + idx_split_count + 1, xmax, ymax))
                else:
                    idx_split_count += rle[i + 1]
                i += 2
        else:
            homogeneous = True
    else:
        homogeneous = True

    if homogeneous:
        splitted_bb.append((xmin, ymin, xmax, ymax))
    splitted_region = np.array_split(region, idx_split, axis=0)

    return homogeneous, splitted_region, splitted_bb


def split_vertical(arr, xmin, ymin, lst=None, lst_bb =None):

    if lst == None and lst_bb == None:
        lst = []
        lst_bb = []
    splitted = vertical_homogeneity(arr, xmin, ymin)
    if splitted[0]:
        arr[arr == 0] = 255
        arr[arr == 1] = 0
        #cv2.imwrite('./split/' + str(len(lst)) + '.png', arr)
        lst.append(arr)
        lst_bb.append(splitted[2])
        return lst, lst_bb
    else:
        for index, item in enumerate(splitted[1]):
            if type(item) is np.ndarray:
                if item.shape[1] > 0 and item.shape[1] > 0 and item[item == 1].size > 0:
                    split_vertical(item, splitted[2][index][0], splitted[2][index][1], lst, lst_bb)
    return lst, lst_bb


def split_horizontal(arr, xmin, ymin, lst=None, lst_bb =None):

    if lst == None:
        lst = []
        lst_bb = []
    splitted = horizontal_homogeneity(arr, xmin, ymin)
    if splitted[0]:
        arr[arr == 0] = 255
        arr[arr == 1] = 0
        lst.append(arr)
        lst_bb.append(splitted[2])
        #cv2.imwrite('./split/' + str(len(lst)) + '.png', arr)
        return lst, lst_bb
    else:
        for index, item in enumerate(splitted[1]):
            if item.shape[1] > 0 and item.shape[1] > 0 and item[item == 1].size > 0:
                split_horizontal(item, splitted[2][index][0], splitted[2][index][1], lst, lst_bb)
    return lst, lst_bb


def run(binary, save=False, path=None):
    binary[binary == 0] = 1
    binary[binary == 255] = 0

    homogeneous_v, bb_v = split_vertical(binary, 0, 0)
    splitted_region = []
    bb_region = []
    homogeneous_region = []

    for i, t in enumerate(homogeneous_v):
        homogeneous_h, bb_h = split_horizontal(t, bb_v[i][0][0], bb_v[i][0][1])
        splitted_region.append(homogeneous_h)
        bb_region.append(bb_h)

    for i, t in enumerate(splitted_region):
        if t is None:
            tmp = [homogeneous_v[i], bb_v[i]]
            homogeneous_region.append(tmp)
            if save:
                cv2.imwrite(path + str(i) + '.png', homogeneous_v[i])
        else:
            for j, tt in enumerate(t):
                tmp = [tt, bb_region[i][j]]
                homogeneous_region.append(tmp)
                if save:
                    cv2.imwrite(path + str(i) + '_' + str(j) + '.png', tt)

    return homogeneous_region
