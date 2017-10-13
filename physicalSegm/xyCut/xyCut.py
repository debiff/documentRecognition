from operator import itemgetter
from collections import OrderedDict


def valleys(cc_list):
    x_sum = {}
    y_sum = {}
    for index in range(0,900): # todo change the range with the dimension of the image
        x_sum[index] = 0
        y_sum[index] =0

    for index, component in cc_list.items():
        x_min, x_max = component.get_x_coordinates()

        for index in range(x_min, x_max):
            x_sum[index] += 1

        y_min, y_max = component.get_y_coordinates()
        for index in range(y_min, y_max):
            y_sum[index] += 1

    return order_dict(x_sum, 1), order_dict(y_sum,1)


def order_dict(dictionary, index):
    return OrderedDict(sorted(dictionary.items(), key=itemgetter(index)))