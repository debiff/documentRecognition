import cv2
import numpy as np
import math
from statistics import median
from MHS import hre
from datetime import datetime


def homogeneity(region):
    return True


def split(region, index, direction):
    return


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
