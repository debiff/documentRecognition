import cv2
import numpy as np
import math
from statistics import median
from MHS import hre
from datetime import datetime


def vertical_homogeneity(region):
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
    splitted_region = []
    idx_split = []
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
                elif countb + 1 >= imaxb and rle[i] == 0:
                    idx_split_count += math.floor((rle[i + 1]) / 2)
                    idx_split.append(idx_split_count)
                    if (i + 5) < rle.size:
                        idx_split_count += math.ceil((rle[i + 1]) / 2) + rle[i + 3] + math.floor((rle[i + 5]) / 2)
                        idx_split.append(idx_split_count)
                    if (i + 3) < rle.size:
                        idx_split_count += rle[i + 1] + rle[i + 3]
                        idx_split.append(idx_split_count)
                    countb += 1
                else:
                    idx_split_count += rle[i + 1]
                i += 2

    if varw > 1.3 and varw > varb:
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
                else:
                    idx_split_count += rle[i + 1]
                i += 2
    splitted_region = np.array_split(region, idx_split, axis=1)

    return varb < 1.3 and varw < 1.3, splitted_region


def horizontal_homogeneity(region):
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
    splitted_region =[]
    idx_split = []
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
                elif countb + 1 >= imaxb and rle[i] == 0:
                    idx_split_count += math.floor((rle[i+1])/2)
                    idx_split.append(idx_split_count)
                    if(i+5) < rle.size:
                        idx_split_count += math.ceil((rle[i+1])/2) + rle[i + 3] + math.floor(rle[i + 5] / 2)
                        idx_split.append(idx_split_count)
                else:
                    idx_split_count += rle[i + 1]
                i += 2

    if varw > 1.3 and varw > varb:
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
                else:
                    idx_split_count += rle[i + 1]
                i += 2
    splitted_region = np.array_split(region, idx_split, axis=0)

    return varb < 1.3 and varw < 1.3, splitted_region


def split_vertical(arr, lst=None):

    if lst == None:
        lst = []
    splitted = vertical_homogeneity(arr)
    if splitted[0]:
        arr[arr == 0] = 255
        arr[arr == 1] = 0
        #cv2.imwrite('./split/' + str(len(lst)) + '.png', arr)
        return lst.append(arr)
    else:
        for index, item in enumerate(splitted[1]):
            if item.shape[1] > 0 and item.shape[1] > 0 and item[item == 1].size > 0:
                split_vertical(item, lst)
    return lst


def split_horizontal(arr, lst=None):

    if lst == None:
        lst = []
    splitted = horizontal_homogeneity(arr)
    if splitted[0]:
        arr[arr == 0] = 255
        arr[arr == 1] = 0
        #cv2.imwrite('./split/' + str(len(lst)) + '.png', arr)
        return lst.append(arr)
    else:
        for index, item in enumerate(splitted[1]):
            if item.shape[1] > 0 and item.shape[1] > 0 and item[item == 1].size > 0:
                split_horizontal(item, lst)
    return lst


def run(binary, save=False, path=None):
    binary[binary == 0] = 1
    binary[binary == 255] = 0
    homogeneous_v = split_vertical(binary)
    splitted_region = []
    homogeneous_region = []

    for i, t in enumerate(homogeneous_v):
        splitted_region.append(split_horizontal(t))

    for i, t in enumerate(splitted_region):
        if t is None:
            homogeneous_region.append(homogeneous_v[i])
            if save:
                cv2.imwrite(path + str(i) + '.png', homogeneous_v[i])
        else:
            for j, tt in enumerate(t):
                homogeneous_region.append(tt)
                if save:
                    cv2.imwrite(path + str(i) + '_' + str(j) + '.png', tt)

    return
