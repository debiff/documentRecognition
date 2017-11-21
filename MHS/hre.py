import numpy as np


def smoothing(arr, window):
    smoothed_list = []
    for i, x in np.ndenumerate(arr):
        tmp = 0
        for w in range(0,window):
            if i[0] - w >= 0:
                tmp = tmp + arr[i[0] - w]
        for w in range(1,window):
            if i[0] + w < arr.size:
                tmp = tmp + arr[i[0] + w]
        smoothed_list.append(tmp/(2*window))
    return np.floor(np.array(smoothed_list))


def local_extremes(arr):
    local_list = []
    for i, x in np.ndenumerate(arr):
        if i[0]+1 < arr.size:
            if ((x < 0) and (arr[i[0] + 1] >= 0)) or ((x > 0) and (arr[i[0] + 1] <= 0)):
                local_list.append(i[0])
    return np.array(local_list)


def distances(arr):
    distance_list = []
    for i, x in np.ndenumerate(arr):
        if i[0] + 1 < arr.size:
            tmp = arr[i[0] + 1] - x
            distance_list.append(tmp)

    return np.array(distance_list)


def separate_b_w(arr):
    b_list = []
    w_list = []
    for i in range(1, arr.size):
        if arr[i] > 0 and arr[i-1] < 0:
            b_list.append(arr[i])
        if arr[i] > 0 and arr[i-1] == 0:
            w_list.append(arr[i])
    return np.array(b_list), np.array(w_list)


def variance(arr):
    mean = np.mean(arr)
    vari = 0
    for i, x in np.ndenumerate(arr):
        vari += (x - mean)**2
    vari = vari / arr.size
    return vari


def switch(from_value, to_value, arr):
    new = np.array(arr, dtype='int64')
    new[new > from_value ] = to_value
    return new


def run_lenght_encoding(arr):
    rle_list = []
    count = 1
    for i,x in np.ndenumerate(arr):
        if i[0] + 1 > arr.size - 1:
            rle_list.append(x)
            rle_list.append(count)
        else:
            if (x == -1 and arr[i[0]+1] == 0) or (x == 0 and arr[i[0]+1] == -1):
                rle_list.append(x)
                rle_list.append(count)
                count = 1
            elif (x == -1 and arr[i[0]+1] == -1) or (x == 0 and arr[i[0] + 1] == 0):
                count +=1
    return np.array(rle_list)
